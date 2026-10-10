#!/usr/bin/env python3
"""Placed figures 01-03 and 05-07 for what-is-a-relational-database-postgresql.
FIG_04 is routed `mermaid` and lives in fig-04-path-of-a-query.mmd (_fig04.py renders it).

Every number is read from lab/captures.json, the run the article quotes, or is arithmetic on
those numbers. Values shown only in captures.md (the EXPLAIN text, the catalog rows) are typed
here exactly as that file prints them.

Run:  python3 _figs.py            # all
      python3 _figs.py 01 06      # only those
"""
import json
import pathlib
import sys

from _build import (ACCENT, ACCENT_TINT, INK, MONO, MUTED, PAPER, RULE, RULE_SOLID,
                    SOFT, SANS, box, cell, emit, eyebrow, legend, masked, mono, node,
                    tag, txt, vline, hline)

HERE = pathlib.Path(__file__).resolve().parent
D = json.loads((HERE.parent / "lab" / "captures.json").read_text())
REV = {c: (int(r), int(n)) for c, r, n in D["revenue_clean"]}
JP_CLEAN, JP_ORDERS = REV["JP"]
DUP = D["dup_amount"]
JP_DUP = JP_CLEAN + DUP
WARN = "#b5452a"


def fmt(n):
    return f"{n:,}"


def note(x, y, text, anchor="start", fill=SOFT, size=8, weight="400"):
    return mono(x, y, text, size=size, fill=fill, anchor=anchor, weight=weight, track="0.02em")


def vh(x1, y1, x2, y2, r=8, stroke=MUTED, sw=1, marker="arrow", dash=None):
    """Vertical from (x1,y1), then horizontal into (x2,y2): arrives head-on at a side edge."""
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    d = f"M {x1} {y1} V {y2 - sy * r} Q {x1} {y2} {x1 + sx * r} {y2} H {x2}"
    m = f' marker-end="url(#{marker})"' if marker else ""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}"{da}{m}/>'


def hvh(x1, y1, xm, y2, x2, r=8, stroke=MUTED, sw=1, marker="arrow", dash=None):
    """Horizontal to xm, vertical to y2, horizontal into x2."""
    sx1 = 1 if xm > x1 else -1
    sx2 = 1 if x2 > xm else -1
    sy = 1 if y2 > y1 else -1
    if abs(y2 - y1) < 2 * r:
        d = f"M {x1} {y1} H {x2}"
    else:
        d = (f"M {x1} {y1} H {xm - sx1 * r} Q {xm} {y1} {xm} {y1 + sy * r} "
             f"V {y2 - sy * r} Q {xm} {y2} {xm + sx2 * r} {y2} H {x2}")
    m = f' marker-end="url(#{marker})"' if marker else ""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}"{da}{m}/>'


def ltag(x, y, s, stroke=INK, w=None):
    """A tag that keeps identifiers in their real (lower) case."""
    w = w or max(28, 6 * len(s) + 14)
    return (f'<rect x="{x}" y="{y}" width="{w}" height="14" rx="2" fill="transparent" '
            f'stroke="{stroke}" stroke-opacity="0.55" stroke-width="0.8"/>'
            + mono(x + w / 2, y + 10, s, size=8, fill=stroke, weight="500"))


def grid_header(x, y, cols, h=24, fill="rgba(45,49,66,0.06)"):
    s, cx = "", x
    for name, w in cols:
        s += (f'<rect x="{cx}" y="{y}" width="{w}" height="{h}" fill="{fill}" '
              f'stroke="rgba(45,49,66,0.30)" stroke-width="0.8"/>')
        s += mono(cx + w / 2, y + h / 2 + 3, name, size=9, fill=INK, weight="600")
        cx += w
    return s


def grid_row(x, y, cols, values, h=26, fill="#ffffff", tcolor=INK, size=10):
    s, cx = "", x
    for (_, w), v in zip(cols, values):
        s += cell(cx, y, w, h, v, fill=fill, tcolor=tcolor, size=size)
        cx += w
    return s


def ellipsis_row(x, y, cols, h=18):
    w = sum(c[1] for c in cols)
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PAPER}" '
            f'stroke="rgba(45,49,66,0.18)" stroke-width="0.8" stroke-dasharray="3,3"/>'
            + mono(x + w / 2, y + h / 2 + 3, "⋯", size=10, fill=SOFT))


# ------------------------------------------------------------------ FIG 01
def fig01():
    """The revenue plan as a tree, bottom-up, from the shipped EXPLAIN ANALYZE."""
    vw, vh_ = 872, 830
    s = eyebrow(32, 40, "the plan postgresql chose · rows flow from the bottom up")
    CX, W, H = 390, 320, 48
    X = CX - W / 2
    spine = [  # (y, name, sub, kind)
        (92, "Sort", "key: revenue_cents desc · actual 5", "backend"),
        (180, "Finalize GroupAggregate", "key: country · actual 5", "backend"),
        (268, "Gather Merge", "Workers Launched: 2 · actual 15", "backend"),
        (372, "Sort", "key: country · actual 5 in each process", "backend"),
        (460, "Partial HashAggregate", "key: country · actual 5 in each process", "backend"),
        (548, "Hash Join", "o.customer_id = c.id · actual 111,111 in each", "focal"),
    ]
    # parallel region first, so the nodes sit on top of it
    s += (f'<rect x="20" y="338" width="830" height="470" rx="10" fill="rgba(45,49,66,0.025)" '
          f'stroke="{SOFT}" stroke-width="1" stroke-dasharray="5,4"/>')
    s += eyebrow(36, 357, "inside each of 3 processes: the leader and 2 workers", fill=MUTED)
    for y, name, sub, kind in spine:
        s += node(X, y, W, H, name, sub, kind=kind)
    labels = ["5 country totals", "15 rows: 5 from each process", "5 sorted rows, from each of 3",
              "5 partial totals", "111,111 joined rows"]
    # result arrow out of the top
    s += vline(CX, 92, 62)
    s += masked(CX + 12, 74, "5 rows, largest first", anchor="start", fill=INK)
    for (y_up, *_), (y_dn, *_), lab in zip(spine[:-1], spine[1:], labels):
        s += vline(CX, y_dn, y_up + H)
        s += masked(CX + 12, (y_dn + y_up + H) / 2 + 3, lab, anchor="start")
    # leaves
    oy, ow, oh = 642, 300, 64
    s += box(32, oy, ow, oh, fill="#ffffff", stroke=INK)
    s += txt(32 + ow / 2, oy + 20, "Parallel Seq Scan on orders", size=12, weight="600")
    s += mono(32 + ow / 2, oy + 37, "filter: status = 'paid' · 7,693 pages", size=9, fill=SOFT)
    s += mono(32 + ow / 2, oy + 53, "estimate 140,514 · actual 111,111 in each", size=9,
              fill=ACCENT, weight="500")
    hx, hy, hw = 560, 642, 260
    s += node(hx, hy, hw, H, "Hash", "lookup table keyed on c.id", kind="store")
    cy_ = 740
    s += node(hx, cy_, hw, H, "Seq Scan on customers", "all 100,000 rows, in each process",
              kind="backend")
    join_mid = 548 + H / 2
    s += vh(32 + ow / 2, oy, X, join_mid)
    s += masked(32 + ow / 2 - 8, 622, "111,111 paid orders", anchor="end")
    s += vh(hx + hw / 2, hy, X + W, join_mid)
    s += masked(hx + hw / 2 + 8, 622, "hash table on c.id", anchor="start")
    s += vline(hx + hw / 2, cy_, hy + H)
    s += masked(hx + hw / 2 + 8, 724, "100,000 customers", anchor="start")
    # verdict
    s += note(32, oy + oh + 26, "the planner guessed 140,514 paid orders per process;", fill=ACCENT)
    s += note(32, oy + oh + 40, "each found 111,111. the guess picks how, never what.", fill=ACCENT)
    return emit("01", "plan-as-a-tree", "The plan for the revenue question",
                "EXPLAIN ANALYZE redrawn as the tree it is. Each step hands its rows to the step above it.",
                "worked example", vw, vh_, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    """What the two tables declare: one primary key, no key, and a link nobody checks."""
    vw, vh_ = 1016, 360
    s = eyebrow(32, 40, "what the two tables declare")
    # customers
    cx0, cy0 = 32, 120
    ccols = [("id", 90), ("name", 170), ("country", 90)]
    s += txt(cx0, 82, "customers", size=15, weight="600", anchor="start")
    s += note(cx0 + 98, 82, "degree 3 · 100,000 rows")
    s += ltag(cx0, 95, "primary key · customers_pkey", stroke=ACCENT)
    s += grid_header(cx0, cy0, ccols)
    s += (f'<rect x="{cx0}" y="{cy0}" width="90" height="24" fill="{ACCENT_TINT}" '
          f'stroke="{ACCENT}" stroke-width="1.2"/>' + mono(cx0 + 45, cy0 + 15, "id", size=9, fill=ACCENT, weight="600"))
    s += ellipsis_row(cx0, cy0 + 24, ccols)
    s += grid_row(cx0, cy0 + 42, ccols, ["92399", "customer 92399", "JP"])
    s += ellipsis_row(cx0, cy0 + 68, ccols)
    s += note(cx0 + 64, cy0 + 112, "declared: unique and never empty,", fill=ACCENT)
    s += note(cx0 + 64, cy0 + 126, "checked on every insert and update", fill=ACCENT)
    # orders
    ox0, oy0 = 470, 120
    ocols = [("id", 70), ("customer_id", 110), ("amount_cents", 120), ("created", 100), ("status", 80)]
    s += txt(ox0, 82, "orders", size=15, weight="600", anchor="start")
    s += note(ox0 + 66, 82, "degree 5 · 1,000,000 rows")
    s += ltag(ox0, 95, "no key", stroke=WARN)
    s += note(ox0 + 80, 105, "an exact copy of a row is accepted", fill=WARN)
    s += grid_header(ox0, oy0, ocols)
    s += ellipsis_row(ox0, oy0 + 24, ocols)
    s += grid_row(ox0, oy0 + 42, ocols, ["4242", "92399", "56954", "⋯", "paid"])
    s += ellipsis_row(ox0, oy0 + 68, ocols)
    # the undeclared foreign key: orders.customer_id 92399 -> customers.id 92399
    fk_x1 = ox0 + 70 + 55          # centre of the customer_id cell
    fk_y1 = oy0 + 42 + 26          # bottom of that cell
    tx = cx0 + 45                  # centre of customers.id cell
    ty = cy0 + 42 + 26
    s += (f'<path d="M {fk_x1} {fk_y1} V {ty + 70} Q {fk_x1} {ty + 78} {fk_x1 - 8} {ty + 78} '
          f'H {tx + 8} Q {tx} {ty + 78} {tx} {ty + 70} V {ty}" fill="none" stroke="{MUTED}" '
          f'stroke-width="1.2" stroke-dasharray="5,4" marker-end="url(#arrow)"/>')
    s += masked((fk_x1 + tx) / 2 + 40, ty + 82, "orders.customer_id = customers.id", fill=INK)
    s += note((fk_x1 + tx) / 2 + 40, ty + 102, "a foreign key in fact · not declared · not checked",
              anchor="middle", fill=WARN)
    # verdict
    s += (f'<line x1="32" y1="{vh_ - 52}" x2="{vw - 32}" y2="{vh_ - 52}" stroke="{RULE}" stroke-width="0.8"/>')
    s += txt(32, vh_ - 28, "Declared, the rule holds for every program that connects. Not declared, it holds only "
             "as long as the data happens to.", size=12, fill=MUTED, anchor="start")
    return emit("02", "declared-keys", "What the two tables declare",
                "customers has a primary key; orders has none, and its link to customers exists only in the data.",
                "what is a relation", vw, vh_, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    """The catalog: your tables as rows of pg_class and pg_attribute, and pg_class as a row of itself."""
    vw, vh_ = 1016, 400
    s = eyebrow(32, 40, "the schema is stored as data")
    # your tables
    s += note(32, 80, "your tables", fill=MUTED, weight="500")
    s += node(32, 96, 150, 48, "customers", "table · 3 columns", kind="backend")
    s += node(32, 196, 150, 48, "orders", "table · 5 columns", kind="backend")
    # pg_class grid
    px, py = 280, 112
    pcols = [("relname", 120), ("relkind", 70), ("relnatts", 80)]
    s += txt(px, 80, "pg_class", size=14, weight="600", anchor="start", family=MONO)
    s += note(px + 82, 80, "one row per table")
    s += grid_header(px, py - 24, pcols)
    prow = [("customers", "r", "3"), ("orders", "r", "5"), ("pg_attribute", "r", "25"), ("pg_class", "r", "34")]
    for i, vals in enumerate(prow):
        focal = vals[0] == "pg_class"
        s += grid_row(px, py + i * 26, pcols, list(vals), fill=ACCENT_TINT if focal else "#ffffff",
                      tcolor=ACCENT if focal else INK)
    # pg_attribute grid (the five columns of orders)
    ax, ay = 640, 112
    acols = [("attrelid", 70), ("attname", 120), ("atttypid", 100), ("attnum", 54)]
    s += txt(ax, 80, "pg_attribute", size=14, weight="600", anchor="start", family=MONO)
    s += note(ax + 118, 80, "one row per column")
    s += grid_header(ax, ay - 24, acols)
    arow = [("orders", "id", "integer", "1"), ("orders", "customer_id", "integer", "2"),
            ("orders", "amount_cents", "integer", "3"), ("orders", "created", "timestamptz", "4"),
            ("orders", "status", "text", "5")]
    for i, vals in enumerate(arow):
        s += grid_row(ax, ay + i * 26, acols, list(vals), size=9)
    # edges: table -> its pg_class row (enter the row's left edge head-on)
    s += hvh(182, 120, 230, py + 13, px, stroke=MUTED)
    s += hvh(182, 220, 246, py + 26 + 13, px, stroke=MUTED)
    s += masked(206, 168, "one row each", anchor="middle")
    # orders -> its five pg_attribute rows: down and around under pg_class, into the left edge
    s += (f'<path d="M 107 244 V 292 Q 107 300 115 300 H 588 Q 596 300 596 292 '
          f'V {ay + 2 * 26 + 21} Q 596 {ay + 2 * 26 + 13} 604 {ay + 2 * 26 + 13} H {ax - 14}" '
          f'fill="none" stroke="{MUTED}" stroke-width="1" marker-end="url(#arrow)"/>')
    s += masked(300, 304, "one row per column: 5 for orders", anchor="middle")
    # bracket on the five rows
    s += (f'<path d="M {ax - 8} {ay} H {ax - 14} V {ay + 5 * 26} H {ax - 8}" fill="none" '
          f'stroke="{SOFT}" stroke-width="0.8"/>')
    # pg_class describes itself: out of its row's bottom edge, back into its right edge
    ry = py + 3 * 26 + 13
    rb = py + 4 * 26
    rx = px + 270
    xs = px + 200
    s += (f'<path d="M {xs} {rb} V {rb + 20} Q {xs} {rb + 28} {xs + 8} {rb + 28} H {rx + 22} '
          f'Q {rx + 30} {rb + 28} {rx + 30} {rb + 20} V {ry + 8} Q {rx + 30} {ry} {rx + 22} {ry} '
          f'H {rx}" fill="none" stroke="{ACCENT}" stroke-width="1.2" marker-end="url(#arrow-accent)"/>')
    s += masked(px + 150, rb + 46, "pg_class is a table, so it has a row in pg_class", fill=ACCENT)
    s += (f'<line x1="32" y1="{vh_ - 52}" x2="{vw - 32}" y2="{vh_ - 52}" stroke="{RULE}" stroke-width="0.8"/>')
    s += txt(32, vh_ - 28, "You read the catalog with the same SQL you use on your own tables.",
             size=12, fill=MUTED, anchor="start")
    return emit("03", "schema-is-data", "The catalog describes your tables, and itself",
                "Every table is a row in pg_class and every column a row in pg_attribute, including the catalog's own.",
                "what is a relation", vw, vh_, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    """System R's four phases (1979) beside PostgreSQL's four stages: three match, one each does not."""
    vw, vh_ = 1016, 640
    s = eyebrow(32, 40, "four phases in 1979, four stages now")
    LX, RX, BW, BH = 220, 590, 230, 50
    s += txt(LX + BW / 2, 82, "System R · 1979", size=14, weight="600")
    s += txt(RX + BW / 2, 82, "PostgreSQL 18", size=14, weight="600")
    rows = [100, 196, 292, 388, 484]
    sr = {0: ("parsing", "checks the syntax"), 2: ("optimization", "looks names up · picks access paths"),
          3: ("code generation", "turns the choice into code"), 4: ("execution", "runs the generated code")}
    pg = {0: ("parser", "grammar, then names (pass 2)"), 1: ("rewriter", "expands views"),
          2: ("planner", "picks the cheapest path"), 4: ("executor", "walks the plan tree")}
    for i, y in enumerate(rows):
        if i in sr:
            name, sub = sr[i]
            s += node(LX, y, BW, BH, name, sub, kind="focal" if i == 3 else "backend")
        if i in pg:
            name, sub = pg[i]
            s += node(RX, y, BW, BH, name, sub, kind="focal" if i == 1 else "backend")
    # within-row flow, with what travels
    def down(x, i0, i1, label, side, gapnote=None):
        out = vline(x, rows[i0] + BH, rows[i1])
        ymid = (rows[i0] + BH + rows[i1]) / 2 + 3
        if side == "left":
            out += masked(x - 10, ymid, label, anchor="end")
        else:
            out += masked(x + 10, ymid, label, anchor="start")
        if gapnote:
            gy = rows[(i0 + i1) // 2] + BH / 2 + 4
            out += note(x + (12 if side == "left" else -12), gy, gapnote,
                        anchor="start" if side == "left" else "end", fill=SOFT)
        return out
    lx, rx = LX + BW / 2, RX + BW / 2
    s += down(lx, 0, 2, "query blocks", "left", gapnote="no rewrite stage")
    s += down(lx, 2, 3, "join order + access paths", "left")
    s += down(lx, 3, 4, "generated code", "left")
    s += down(rx, 0, 1, "query tree", "right")
    s += down(rx, 1, 2, "rewritten query tree", "right")
    s += down(rx, 2, 4, "plan tree", "right", gapnote="no code-generation stage")
    # matched pairs
    for i in (0, 2, 4):
        y = rows[i] + BH / 2
        s += (f'<line x1="{LX + BW}" y1="{y}" x2="{RX}" y2="{y}" stroke="{RULE_SOLID}" '
              f'stroke-width="1" stroke-dasharray="2,3"/>')
        s += masked((LX + BW + RX) / 2, y + 3, "same job", fill=SOFT)
    s += (f'<line x1="32" y1="{vh_ - 76}" x2="{vw - 32}" y2="{vh_ - 76}" stroke="{RULE}" stroke-width="0.8"/>')
    s += txt(32, vh_ - 50, "Three phases match. Each list has one step the other lacks: System R generated code,",
             size=12, fill=MUTED, anchor="start")
    s += txt(32, vh_ - 30, "PostgreSQL rewrites views. And the name lookups moved from the optimizer to the parser.",
             size=12, fill=MUTED, anchor="start")
    return emit("05", "system-r-vs-postgresql", "Four phases in 1979, four stages now",
                "System R's statement processing (Selinger et al., 1979) beside PostgreSQL's path of a query.",
                "from query to rows", vw, vh_, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    """One duplicated order, one customer, two joined rows, one total off by the order's amount."""
    vw, vh_ = 1016, 440
    s = eyebrow(32, 40, "how one duplicate moves a total")
    # orders: the same row twice
    ox = 32
    ocols = [("id", 50), ("customer_id", 90), ("amount_cents", 100), ("status", 56)]
    s += txt(ox, 86, "orders", size=14, weight="600", anchor="start")
    s += note(ox + 62, 86, "no key")
    s += grid_header(ox, 100, ocols)
    r1, r2 = 124, 162
    for y in (r1, r2):
        s += grid_row(ox, y, ocols, ["4242", "92399", fmt(DUP), "paid"], fill=ACCENT_TINT)
    s += ltag(ox, 198, "the same row, twice", stroke=ACCENT)
    # customers: one row, tall enough to take two edges apart
    cx = 480
    ccols = [("id", 70), ("country", 66)]
    s += txt(cx, 104, "customers", size=14, weight="600", anchor="start")
    s += grid_header(cx, 118, ccols)
    s += grid_row(cx, 142, ccols, ["92399", "JP"], h=40)
    # join output
    jx = 800
    jcols = [("country", 66), ("amount", 90)]
    s += txt(jx, 86, "join output", size=14, weight="600", anchor="start")
    s += grid_header(jx, 100, jcols)
    for y in (r1, r2):
        s += grid_row(jx, y, jcols, ["JP", fmt(DUP)], fill=ACCENT_TINT)
    # each copy matches the one customer: two edges, two arrowheads
    s += hvh(ox + 296, r1 + 13, 404, 152, cx)
    s += hvh(ox + 296, r2 + 13, 420, 175, cx)
    s += masked(364, r1 + 16, "copy 1")
    s += masked(364, r2 + 16, "copy 2")
    s += note(ox + 296 + 76, 226, "customer_id = id, twice", anchor="middle")
    # each match becomes one joined row
    s += hvh(cx + 136, 152, 708, r1 + 13, jx, r=4)   # small radius: the drop is only 15 px
    s += hvh(cx + 136, 172, 724, 172, jx)
    s += masked(662, 155, "JP · " + fmt(DUP))
    s += masked(662, 175, "JP · " + fmt(DUP))
    # both joined rows are summed
    sx, sy, sw_, sh = 480, 262, 504, 92
    s += vline(jx + 78, r2 + 26, sy)
    s += masked(jx + 88, 230, "both rows are summed", anchor="start")
    s += box(sx, sy, sw_, sh, fill=ACCENT_TINT, stroke=ACCENT)
    s += eyebrow(sx + 16, sy + 22, "sum(amount_cents) for JP", fill=ACCENT)
    s += mono(sx + 16, sy + 50, f"{fmt(JP_CLEAN)} + {fmt(DUP)} = {fmt(JP_DUP)}", size=15,
              fill=INK, anchor="start", weight="600")
    s += mono(sx + 16, sy + 74, f"paid orders {fmt(JP_ORDERS)} → {fmt(JP_ORDERS + 1)} · no error, no warning",
              size=10, fill=MUTED, anchor="start")
    # what a key changes
    s += box(32, sy, 400, sh, fill="#ffffff", stroke=INK)
    s += eyebrow(48, sy + 22, "with primary key (id) declared", fill=MUTED)
    s += mono(48, sy + 46, "the second insert is refused:", size=10, fill=INK, anchor="start")
    s += mono(48, sy + 64, "duplicate key value violates", size=10, fill=WARN, anchor="start")
    s += mono(48, sy + 80, 'unique constraint "orders_pkey"', size=10, fill=WARN, anchor="start")
    s += (f'<line x1="32" y1="{vh_ - 56}" x2="{vw - 32}" y2="{vh_ - 56}" stroke="{RULE}" stroke-width="0.8"/>')
    s += txt(32, vh_ - 30, "The query is correct. The data broke a rule nobody declared.",
             size=12, fill=MUTED, anchor="start")
    return emit("06", "duplicate-row", "How one duplicate moves a total",
                "Order 4242 stored twice: both copies find customer 92399, so the sum counts the amount twice.",
                "two surprises", vw, vh_, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    """NULL in a comparison (three-valued WHERE) and in a count."""
    vw, vh_ = 1016, 420
    s = eyebrow(32, 40, "null in a comparison and in a count")
    # left: truth grid
    gx, gy = 32, 110
    s += txt(gx, 84, "which rows does WHERE keep?", size=14, weight="600", anchor="start")
    rowh, lw, cw = 34, 220, 140
    heads = ["amount_cents = NULL", "amount_cents IS NULL"]
    for j, h in enumerate(heads):
        x = gx + lw + j * cw
        s += (f'<rect x="{x}" y="{gy}" width="{cw}" height="28" fill="rgba(45,49,66,0.06)" '
              f'stroke="rgba(45,49,66,0.30)" stroke-width="0.8"/>')
        s += mono(x + cw / 2, gy + 18, h, size=8.5, fill=INK, weight="600")
    body = [(f"{fmt(D['count_amount'])} rows with an amount", ["unknown", "false"]),
            ("1 row whose amount is NULL", ["unknown", "true"])]
    for i, (lab, vals) in enumerate(body):
        y = gy + 28 + i * rowh
        s += (f'<rect x="{gx}" y="{y}" width="{lw}" height="{rowh}" fill="#ffffff" '
              f'stroke="rgba(45,49,66,0.30)" stroke-width="0.8"/>')
        s += mono(gx + 10, y + rowh / 2 + 3, lab, size=9, fill=INK, anchor="start")
        for j, v in enumerate(vals):
            x = gx + lw + j * cw
            hot = v == "true"
            s += cell(x, y, cw, rowh, v.upper(), fill=ACCENT_TINT if hot else "#ffffff",
                      tcolor=ACCENT if hot else (SOFT if v == "unknown" else MUTED), size=10)
    y = gy + 28 + 2 * rowh
    s += (f'<rect x="{gx}" y="{y}" width="{lw}" height="{rowh}" fill="rgba(45,49,66,0.06)" '
          f'stroke="rgba(45,49,66,0.30)" stroke-width="0.8"/>')
    s += mono(gx + 10, y + rowh / 2 + 3, "rows kept (TRUE only)", size=9, fill=INK, anchor="start", weight="600")
    for j, v in enumerate([D["eq_null_rows"], D["is_null_rows"]]):
        x = gx + lw + j * cw
        s += cell(x, y, cw, rowh, str(v), fill="rgba(45,49,66,0.06)", tcolor=INK, size=12, weight="600")
    s += note(gx, y + rowh + 24, "a comparison with NULL is UNKNOWN, and WHERE discards UNKNOWN like FALSE")
    # right: the two counts
    rx = 600
    s += txt(rx, 84, "two counts over the same rows", size=14, weight="600", anchor="start")
    s += box(rx, 110, 384, 78, fill="#ffffff", stroke=INK)
    s += mono(rx + 16, 138, "count(*)", size=11, fill=INK, anchor="start", weight="600")
    s += mono(rx + 368, 140, fmt(D["count_star"]), size=18, fill=INK, anchor="end", weight="600")
    s += note(rx + 16, 170, "counts rows")
    s += box(rx, 204, 384, 78, fill=ACCENT_TINT, stroke=ACCENT)
    s += mono(rx + 16, 232, "count(amount_cents)", size=11, fill=ACCENT, anchor="start", weight="600")
    s += mono(rx + 368, 234, fmt(D["count_amount"]), size=18, fill=ACCENT, anchor="end", weight="600")
    s += note(rx + 16, 264, "counts values that are not NULL", fill=ACCENT)
    s += note(rx, 310, f"the difference is order 4242, the one blanked amount;")
    s += note(rx, 324, "sum() and avg() skip it the same way")
    s += (f'<line x1="32" y1="{vh_ - 56}" x2="{vw - 32}" y2="{vh_ - 56}" stroke="{RULE}" stroke-width="0.8"/>')
    s += txt(32, vh_ - 30, "NULL is not a value. It is a marker for unknown, and unknown changes both answers.",
             size=12, fill=MUTED, anchor="start")
    return emit("07", "three-valued-logic", "NULL in a comparison and in a count",
                "= NULL is never true, so it matches nothing; count(column) skips the row whose value is unknown.",
                "two surprises", vw, vh_, s)


ALL = {"01": fig01, "02": fig02, "03": fig03, "05": fig05, "06": fig06, "07": fig07}

if __name__ == "__main__":
    for k in sys.argv[1:] or sorted(ALL):
        ALL[k]()
