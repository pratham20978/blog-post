#!/usr/bin/env python3
"""Placed figures 01-10 for sql-select-evaluation-joins-group-by-null.

The sample's rows are parsed from lab/sample.sql and every full-scale number is read from
lab/captures.json, the run the article quotes, or is arithmetic on those numbers.

Run:  python3 _figs.py            # all
      python3 _figs.py 01 06      # only those
"""
import json
import pathlib
import re
import sys

from _build import (ACCENT, ACCENT_TINT, INK, MONO, MUTED, PAPER, RULE, RULE_SOLID,
                    SOFT, box, cell, emit, eyebrow, masked, mono, node, txt, vline, hline)

HERE = pathlib.Path(__file__).resolve().parent
LAB = HERE.parent / "lab"
D = json.loads((LAB / "captures.json").read_text())
F, S = D["full"], D["sample"]
WARN = "#b5452a"
WARN_TINT = "rgba(181,69,42,0.08)"
GREY_TINT = "rgba(45,49,66,0.06)"

_sql = (LAB / "sample.sql").read_text()
CUSTOMERS = [(int(i), c) for i, c in re.findall(r"\((\d+), 'customer \d+', '([A-Z]{2})'\)", _sql)]
ORDERS = [(int(i), int(c), int(a), st) for i, c, a, st in
          re.findall(r"\((\d+), (\d+), (\d+), '[^']+', '(\w+)'\)", _sql)]
COUNTRY = dict(CUSTOMERS)


def fmt(n):
    return f"{n:,}"


def note(x, y, text, anchor="start", fill=SOFT, size=8, weight="400"):
    return mono(x, y, text, size=size, fill=fill, anchor=anchor, weight=weight, track="0.02em")


def ltag(x, y, s, stroke=INK, w=None):
    """A tag that keeps identifiers in their real (lower) case."""
    w = w or max(28, 6 * len(s) + 14)
    return (f'<rect x="{x}" y="{y}" width="{w}" height="14" rx="2" fill="transparent" '
            f'stroke="{stroke}" stroke-opacity="0.55" stroke-width="0.8"/>'
            + mono(x + w / 2, y + 10, s, size=8, fill=stroke, weight="500"))


def grid_header(x, y, cols, h=22, fill=GREY_TINT):
    s, cx = "", x
    for name, w in cols:
        s += (f'<rect x="{cx}" y="{y}" width="{w}" height="{h}" fill="{fill}" '
              f'stroke="rgba(45,49,66,0.30)" stroke-width="0.8"/>')
        s += mono(cx + w / 2, y + h / 2 + 3, name, size=8.5, fill=INK, weight="600")
        cx += w
    return s


def grid_row(x, y, cols, values, h=22, fill="#ffffff", tcolor=INK, size=9.5, colors=None):
    s, cx = "", x
    for i, ((_, w), v) in enumerate(zip(cols, values)):
        c = (colors or {}).get(i, tcolor)
        s += cell(cx, y, w, h, v, fill=fill, tcolor=c, size=size)
        cx += w
    return s


def bracket(x, y1, y2, side="right", stroke=SOFT, arm=6):
    """A square bracket spanning y1..y2, opening toward the rows it marks."""
    a = -arm if side == "right" else arm
    return (f'<path d="M {x + a} {y1} H {x} V {y2} H {x + a}" fill="none" stroke="{stroke}" '
            f'stroke-width="1"/>')


def verdict(vw, vh_, text, text2=None):
    s = f'<line x1="32" y1="{vh_ - (74 if text2 else 52)}" x2="{vw - 32}" y2="{vh_ - (74 if text2 else 52)}" stroke="{RULE}" stroke-width="0.8"/>'
    if text2:
        s += txt(32, vh_ - 48, text, size=12, fill=MUTED, anchor="start")
        s += txt(32, vh_ - 28, text2, size=12, fill=MUTED, anchor="start")
    else:
        s += txt(32, vh_ - 28, text, size=12, fill=MUTED, anchor="start")
    return s


def tile(x, y, label, w=34, h=26, fill="#ffffff", stroke="rgba(45,49,66,0.40)", tcolor=INK,
         dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="1"{d}/>' + mono(x + w / 2, y + h / 2 + 4, label, size=10, fill=tcolor,
                                             weight="600"))


# ------------------------------------------------------------------ FIG 01
def fig01():
    """The 20-row sample, with the three things it was built to show."""
    vw, vh_ = 1016, 520
    s = eyebrow(32, 40, "the 20-row sample · 6 customers, 14 orders")
    # customers
    cx, cy = 32, 104
    ccols = [("id", 44), ("name", 112), ("country", 66)]
    s += txt(cx, 82, "customers", size=14, weight="600", anchor="start")
    s += grid_header(cx, cy, ccols)
    for i, (cid, ctry) in enumerate(CUSTOMERS):
        y = cy + 22 + i * 22
        none = cid == 6
        s += grid_row(cx, y, ccols, [str(cid), f"customer {cid}", ctry],
                      fill=WARN_TINT if none else "#ffffff", tcolor=WARN if none else INK)
    y6 = cy + 22 + 5 * 22
    s += ltag(cx + 230, y6 + 4, "no orders", stroke=WARN)
    s += note(cx, cy + 22 + 6 * 22 + 22, "customer 6 matches nothing in a join,", fill=WARN)
    s += note(cx, cy + 22 + 6 * 22 + 36, "so INNER and LEFT JOIN differ by one row", fill=WARN)
    # orders
    ox, oy = 360, 104
    ocols = [("id", 50), ("customer_id", 96), ("country", 64), ("amount_cents", 104), ("status", 80)]
    s += txt(ox, 82, "orders", size=14, weight="600", anchor="start")
    s += note(ox + 60, 82, "country shown for reading; it lives in customers")
    s += grid_header(ox, oy, ocols)
    paid_rows = {}
    for i, (oid, cid, amt, st) in enumerate(ORDERS):
        y = oy + 22 + i * 22
        paid = st == "paid"
        fill = ACCENT_TINT if paid else "#ffffff"
        s += grid_row(ox, y, ocols, [str(oid), str(cid), COUNTRY[cid], fmt(amt), st],
                      fill=fill, colors={4: ACCENT if paid else MUTED})
        if paid:
            paid_rows[oid] = y
    # customer 1's two paid orders
    bx = ox + sum(w for _, w in ocols) + 10
    y101, y102 = paid_rows[101], paid_rows[102]
    s += bracket(bx, y101 + 3, y102 + 19, side="right", stroke=ACCENT)
    s += note(bx + 10, y101 + 14, "customer 1: two paid orders,", fill=ACCENT)
    s += note(bx + 10, y101 + 28, "so a join repeats customer 1 twice", fill=ACCENT)
    # paid revenue per country, worked by hand
    px, py = 792, 300
    s += eyebrow(px, py - 12, "paid revenue, by hand", fill=MUTED)
    lines = [("DE", "5,000 + 3,000 + 1,500", "9,500", INK),
             ("IN", "7,000", "7,000", ACCENT),
             ("JP", "6,000 + 1,000", "7,000", ACCENT)]
    for i, (c, expr, tot, col) in enumerate(lines):
        y = py + 10 + i * 24
        s += mono(px, y, c, size=10, fill=col, anchor="start", weight="600")
        s += mono(px + 26, y, expr, size=9, fill=MUTED, anchor="start")
        s += mono(px + 196, y, tot, size=10, fill=col, anchor="end", weight="600")
    s += note(px, py + 92, "IN and JP tie at 7,000:", fill=ACCENT)
    s += note(px, py + 106, "\"top two\" has no unique answer", fill=ACCENT)
    s += verdict(vw, vh_, "Twenty rows you can count by hand, chosen so that every effect in this post shows up at least once.")
    return emit("01", "sample-rows", "The 20-row sample",
                "Six customers and fourteen orders, with the same columns as the full shop.",
                "worked example", vw, vh_, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    """The logical order, written position on the left, row counts on the right."""
    vw, vh_ = 1016, 800
    s = eyebrow(32, 40, "the order sql evaluates a select · paid revenue per country, top two")
    steps = [  # name, what it does, written position, sample, full
        ("FROM · JOIN", "pairs each order with its customer", "2nd", "14 rows", fmt(F["inner_join"]) + " rows"),
        ("WHERE", "o.status = 'paid' keeps paid orders", "3rd", f"{S['where_paid']} rows", fmt(F["where_paid"]) + " rows"),
        ("GROUP BY", "one row per country; count(*) and sum()", "4th", f"{S['groups']} groups", f"{F['groups']} groups"),
        ("HAVING", "none in this query: every group passes", "5th", f"{S['groups']} groups", f"{F['groups']} groups"),
        ("SELECT", "computes country, paid_orders, revenue_cents", "1st", "3 rows · 3 columns", "5 rows · 3 columns"),
        ("DISTINCT", "none in this query", "with SELECT", "3 rows", "5 rows"),
        ("ORDER BY", "revenue_cents desc: IN and JP tie", "6th", "3 rows, sorted", "5 rows, sorted"),
        ("LIMIT 2", "keeps the first two", "7th", "2 rows", "2 rows"),
    ]
    BX, BW, BH, Y0, GAP = 250, 380, 50, 96, 26
    ys, y = [], Y0
    for name, *_ in steps:
        ys.append(y)
        y += BH + (64 if name == "SELECT" else GAP)
    s += note(BX - 98, Y0 - 16, "written", anchor="middle", fill=MUTED, weight="500")
    s += note(BX + BW + 96, Y0 - 16, "sample", anchor="middle", fill=MUTED, weight="500")
    s += note(BX + BW + 236, Y0 - 16, "full shop", anchor="middle", fill=MUTED, weight="500")
    for i, (name, sub, written, sm, full) in enumerate(steps):
        y = ys[i]
        focal = name == "SELECT"
        s += node(BX, y, BW, BH, name, sub, kind="focal" if focal else "backend")
        s += ltag(BX - 150, y + BH / 2 - 7, written, stroke=ACCENT if focal else MUTED, w=104)
        s += mono(BX + BW + 96, y + BH / 2 + 4, sm, size=10, fill=INK, weight="500")
        s += mono(BX + BW + 236, y + BH / 2 + 4, full, size=10, fill=INK, weight="600")
        if i:
            s += vline(BX + BW / 2, ys[i - 1] + BH, y)
    ysel = ys[4] + BH
    s += note(BX + BW / 2 + 12, ysel + 22, "written first, evaluated fifth: an alias made here", fill=ACCENT)
    s += note(BX + BW / 2 + 12, ysel + 36, "exists in ORDER BY, not in WHERE", fill=ACCENT)
    s += verdict(vw, vh_, "Each clause takes a table and hands one on. Counting the rows at each step predicts the result.",
                 "The order defines the result, not the work: the planner may do the steps in another order.")
    return emit("02", "logical-order", "The logical order of a SELECT",
                "Written order beside evaluation order, with the report's row count after each clause.",
                "worked example", vw, vh_, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    """The tie on the LIMIT 2 boundary, and which plan kept which row."""
    vw, vh_ = 1016, 470
    s = eyebrow(32, 40, "order by revenue_cents desc limit 2 · full shop")
    rows = F["report_ordered"]
    gx, gy = 108, 92
    cols = [("rank", 48), ("country", 72), ("paid_orders", 96), ("revenue_cents", 140)]
    s += grid_header(gx, gy, cols)
    tied = {"IN", "JP"}
    for i, (c, n, rev) in enumerate(rows):
        y = gy + 22 + i * 30
        rank = "1" if i == 0 else ("2 or 3" if c in tied else str(i + 1))
        hot = c in tied
        s += grid_row(gx, y, cols, [rank, c, fmt(n), fmt(rev)], h=30,
                      fill=ACCENT_TINT if hot else "#ffffff", tcolor=ACCENT if hot else INK)
    # the boundary between row 2 and row 3, cutting the tie
    by = gy + 22 + 2 * 30
    wtot = sum(w for _, w in cols)
    s += (f'<line x1="32" y1="{by}" x2="{gx + wtot}" y2="{by}" stroke="{WARN}" '
          f'stroke-width="1.6" stroke-dasharray="6,4"/>')
    s += mono(34, by - 7, "LIMIT 2", size=9, fill=WARN, anchor="start", weight="600")
    s += bracket(gx + wtot + 10, gy + 22 + 30 + 4, gy + 22 + 3 * 30 - 4, side="right", stroke=ACCENT)
    s += note(gx + wtot + 18, gy + 22 + 60 - 18, "same revenue:", fill=ACCENT)
    s += note(gx + wtot + 18, gy + 22 + 60 - 4, "3,333,366,679", fill=ACCENT, weight="600")
    # outcomes
    ox, ow, oh = 600, 384, 78
    sec = F["second_row_by_plan"]
    outs = [
        ("default settings", f"groups reach the sort as {', '.join(F['group_order_default'])}",
         f"DE, {sec['default']}", "backend"),
        ("max_parallel_workers_per_gather = 0", f"a hash aggregate hands them on as {', '.join(F['group_order_no_parallel'])}",
         f"DE, {sec['max_parallel_workers_per_gather = 0']}", "backend"),
        ("fetch first 2 rows with ties", "keeps every row that ties with the last one kept",
         ", ".join(r[0] for r in F["with_ties"]), "focal"),
    ]
    for i, (title, sub, got, kind) in enumerate(outs):
        y = 92 + i * (oh + 18)
        stroke = ACCENT if kind == "focal" else INK
        s += box(ox, y, ow, oh, fill=ACCENT_TINT if kind == "focal" else "#ffffff", stroke=stroke)
        s += mono(ox + 16, y + 22, title, size=10, fill=stroke, anchor="start", weight="600")
        s += note(ox + 16, y + 42, sub, fill=MUTED)
        s += mono(ox + 16, y + 64, "returns: " + got, size=11, fill=INK, anchor="start", weight="600")
    s += verdict(vw, vh_, "The same query, the same rows, two different second places. Neither is wrong:",
                 "the query never said how to break the tie. A tiebreaker or WITH TIES does.")
    return emit("03", "limit-tie", "A tie on the LIMIT boundary",
                "IN and JP have the same paid revenue; which one LIMIT 2 keeps depends on the plan.",
                "worked example", vw, vh_, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    """The left join of the sample: the inner join's 14 rows plus customer 6, padded."""
    vw, vh_ = 1016, 560
    s = eyebrow(32, 40, "customers left join orders on o.customer_id = c.id · the sample")
    gx, gy = 150, 80
    cols = [("c.id", 50), ("c.country", 78), ("o.id", 56), ("o.amount_cents", 116), ("o.status", 86)]
    s += grid_header(gx, gy, cols)
    joined = sorted(ORDERS, key=lambda o: (o[1], o[0]))
    for i, (oid, cid, amt, st) in enumerate(joined):
        y = gy + 22 + i * 22
        s += grid_row(gx, y, cols, [str(cid), COUNTRY[cid], str(oid), fmt(amt), st])
    yp = gy + 22 + len(joined) * 22
    s += grid_row(gx, yp, cols, ["6", "IN", "NULL", "NULL", "NULL"], fill=WARN_TINT,
                  colors={2: WARN, 3: WARN, 4: WARN})
    wtot = sum(w for _, w in cols)
    # brackets: inner join = 14 matched rows; left join = all 15
    s += bracket(gx - 12, gy + 24, yp - 2, side="left", stroke=INK)
    s += mono(gx - 22, gy + 22 + 7 * 22, "INNER JOIN", size=9, fill=INK, anchor="end", weight="600")
    s += note(gx - 22, gy + 22 + 7 * 22 + 14, "14 rows", anchor="end", fill=INK)
    s += bracket(gx + wtot + 12, gy + 24, yp + 20, side="right", stroke=WARN)
    s += mono(gx + wtot + 22, gy + 22 + 7 * 22, "LEFT JOIN", size=9, fill=WARN, anchor="start", weight="600")
    s += note(gx + wtot + 22, gy + 22 + 7 * 22 + 14, "15 rows: the same 14,", anchor="start", fill=WARN)
    s += note(gx + wtot + 22, gy + 22 + 7 * 22 + 28, "plus one padded row", anchor="start", fill=WARN)
    s += note(gx + wtot + 22, yp + 15, "customer 6 matched nothing: its order", anchor="start", fill=WARN)
    s += note(gx + wtot + 22, yp + 29, "columns are filled with NULL", anchor="start", fill=WARN)
    # full scale
    fx, fy = 720, 110
    s += box(fx, fy, 264, 104, fill="#ffffff", stroke=MUTED)
    s += eyebrow(fx + 14, fy + 22, "full shop", fill=MUTED)
    s += mono(fx + 14, fy + 48, f"inner join  {fmt(F['inner_join'])}", size=11, fill=INK, anchor="start", weight="600")
    s += mono(fx + 14, fy + 70, f"left join   {fmt(F['left_join'])}", size=11, fill=WARN, anchor="start", weight="600")
    s += note(fx + 14, fy + 90, f"{fmt(F['padded_rows'])} padded rows, one per new customer")
    s += verdict(vw, vh_, "A left join is the inner join plus one row for each left row that matched nothing.")
    return emit("04", "inner-vs-left-join", "Inner join against left join",
                "The left join keeps customer 6, with NULL in every column that comes from orders.",
                "what does from build", vw, vh_, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    """Customer 6's padded row with the paid condition in ON, and in WHERE."""
    vw, vh_ = 1016, 470
    s = eyebrow(32, 40, "the same condition in two places · customer 6")
    lanes = [
        ("in ON", "left join orders o", "on o.customer_id = c.id and o.status = 'paid'",
         "no paid order matches customer 6", "the row is padded and kept",
         True, S["left_join_on_paid"], F["left_join_on_paid"]),
        ("in WHERE", "left join orders o on o.customer_id = c.id", "where o.status = 'paid'",
         "padded row: status is NULL", "NULL = 'paid' is UNKNOWN: dropped",
         False, S["left_join_where_paid"], F["left_join_where_paid"]),
    ]
    for i, (tagname, l1, l2, mid, res, kept, sn, fn) in enumerate(lanes):
        y = 88 + i * 150
        s += ltag(32, y - 4, f"condition {tagname}", stroke=ACCENT if kept else WARN, w=130)
        s += box(32, y + 20, 300, 64, fill="#ffffff", stroke=INK)
        s += mono(46, y + 44, l1, size=9, fill=INK, anchor="start")
        s += mono(46, y + 62, l2, size=9, fill=ACCENT if kept else INK, anchor="start",
                  weight="600" if kept else "400")
        # the padded row
        rx, rw = 400, 260
        cols = [("c.id", 50), ("country", 70), ("o.id", 60), ("o.status", 80)]
        s += grid_header(rx, y + 20, cols)
        s += grid_row(rx, y + 42, cols, ["6", "IN", "NULL", "NULL"], fill=WARN_TINT,
                      colors={2: WARN, 3: WARN})
        s += note(rx, y + 82, mid, fill=MUTED)
        s += hline(332, rx, y + 52)
        # result
        qx = 730
        stroke = ACCENT if kept else WARN
        s += box(qx, y + 20, 254, 64, fill=ACCENT_TINT if kept else WARN_TINT, stroke=stroke)
        s += mono(qx + 14, y + 42, res, size=9, fill=stroke, anchor="start", weight="600")
        s += mono(qx + 14, y + 64, f"sample {sn} rows · full {fmt(fn)}", size=9, fill=INK, anchor="start")
        s += hline(rx + rw, qx, y + 52)
    s += note(400, 88 + 150 + 104, f"the result equals the inner join's {fmt(F['where_paid'])}:", fill=MUTED)
    s += note(400, 88 + 150 + 118, "the planner dropped the left join from the plan", fill=MUTED)
    s += verdict(vw, vh_, "ON decides what counts as a match, before the padding. WHERE filters afterwards,",
                 "and a padded row's NULLs never satisfy it. For an inner join the two are the same.")
    return emit("05", "on-versus-where", "The same condition in ON and in WHERE",
                "With the paid condition in ON, customer 6 survives; in WHERE, its padded row is dropped.",
                "what does from build", vw, vh_, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    """WHERE against HAVING on the same predicate: two logical paths, one physical plan."""
    vw, vh_ = 1016, 470
    s = eyebrow(32, 40, "status = 'paid' as a row filter and as a group filter · full shop")
    BW, BH = 170, 52
    xs = [32, 262, 492, 722]
    paths = [
        ("WHERE", [(fmt(F["inner_join"]) + " rows", "customers ⋈ orders", "backend"),
                   ("WHERE", "status = 'paid'", "focal"),
                   (fmt(F["rows_into_grouping_where"]) + " rows", "reach grouping", "backend"),
                   ("GROUP BY", f"{F['groups_formed_where']} groups formed", "backend")]),
        ("HAVING", [(fmt(F["inner_join"]) + " rows", "customers ⋈ orders", "backend"),
                    ("GROUP BY", f"{F['groups_formed_having']} groups formed", "backend"),
                    ("HAVING", "status = 'paid'", "focal"),
                    (f"{F['groups_formed_where']} groups", "kept, 10 discarded", "backend")]),
    ]
    for p, (label, nodes) in enumerate(paths):
        y = 92 + p * 130
        s += ltag(32, y - 22, f"as {label}", stroke=MUTED, w=86)
        for i, (name, sub, kind) in enumerate(nodes):
            s += node(xs[i], y, BW, BH, name, sub, kind=kind)
            if i:
                s += hline(xs[i - 1] + BW, xs[i], y + BH / 2)
    # converge on the same answer
    s += txt(976, 145, "same", size=11, fill=MUTED, anchor="middle")
    s += txt(976, 161, "5 rows", size=11, fill=INK, anchor="middle", weight="600")
    s += f'<path d="M {722 + BW} {92 + BH / 2} H 940" fill="none" stroke="{RULE_SOLID}" stroke-width="1"/>'
    s += f'<path d="M {722 + BW} {222 + BH / 2} H 940" fill="none" stroke="{RULE_SOLID}" stroke-width="1"/>'
    s += f'<line x1="940" y1="{92 + BH / 2}" x2="940" y2="{222 + BH / 2}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    # the one physical plan
    py = 300
    s += box(32, py, 952, 64, fill=ACCENT_TINT, stroke=ACCENT)
    s += eyebrow(48, py + 22, "what postgresql ran, both times", fill=ACCENT)
    s += mono(48, py + 46, "Parallel Seq Scan on orders · Filter: (status = 'paid'::text)  →  hash join  →  group by country",
              size=10, fill=INK, anchor="start", weight="500")
    s += verdict(vw, vh_, "Logically, WHERE groups 333,333 rows and HAVING groups 1,000,000. Physically, the planner moved",
                 "the HAVING condition into WHERE, because it uses no aggregate. The plans were identical.")
    return emit("06", "where-versus-having", "WHERE against HAVING",
                "The same condition as a row filter and as a group filter: two logical paths, one plan.",
                "where or having", vw, vh_, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    """The 20 country-and-status groups in DESC order: the NULL groups first."""
    vw, vh_ = 1016, 640
    s = eyebrow(32, 40, "left join, group by country, status, order by revenue_cents desc · full shop")
    nulls = F["status_report_top5"]
    real = [r for r in F["status_report_nulls_last_all"] if r[1] is not None]
    ranked = nulls + real
    gx, gy = 150, 80
    cols = [("rank", 46), ("country", 70), ("status", 90), ("orders", 80), ("revenue_cents", 140)]
    s += grid_header(gx, gy, cols)
    tie = {("JP", "paid"), ("IN", "paid")}
    for i, (c, st, n, rev) in enumerate(ranked):
        y = gy + 22 + i * 22
        isnull = st is None
        hot = (c, st) in tie
        fill = WARN_TINT if isnull else (ACCENT_TINT if hot else "#ffffff")
        tc = WARN if isnull else (ACCENT if hot else INK)
        s += grid_row(gx, y, cols, [str(i + 1), c, "NULL" if isnull else st, fmt(n),
                                    "NULL" if rev is None else fmt(rev)], fill=fill, tcolor=tc)
    wtot = sum(w for _, w in cols)
    # default: the top five are the NULL groups
    s += bracket(gx - 12, gy + 24, gy + 22 + 5 * 22 - 2, side="left", stroke=WARN)
    s += mono(gx - 22, gy + 22 + 2 * 22 + 4, "LIMIT 5", size=9, fill=WARN, anchor="end", weight="600")
    s += note(gx - 22, gy + 22 + 2 * 22 + 18, "five empty", anchor="end", fill=WARN)
    s += note(gx - 22, gy + 22 + 2 * 22 + 32, "groups", anchor="end", fill=WARN)
    # nulls last: the real top five, and the tie for fifth
    y5 = gy + 22 + 5 * 22
    s += bracket(gx + wtot + 12, y5 + 2, y5 + 5 * 22 - 2, side="right", stroke=INK)
    s += mono(gx + wtot + 22, y5 + 2 * 22 + 4, "NULLS LAST, LIMIT 5", size=9, fill=INK, anchor="start", weight="600")
    s += note(gx + wtot + 22, y5 + 2 * 22 + 18, "the real top five", anchor="start", fill=INK)
    s += bracket(gx + wtot + 30, y5 + 4 * 22 + 2, y5 + 6 * 22 - 2, side="right", stroke=ACCENT)
    s += note(gx + wtot + 40, y5 + 5 * 22 + 4, "JP paid and IN paid tie for fifth:", anchor="start", fill=ACCENT)
    s += note(gx + wtot + 40, y5 + 5 * 22 + 18, "WITH TIES returns both", anchor="start", fill=ACCENT)
    s += note(gx + wtot + 22, gy + 34, "each NULL group: 200 padded rows,", anchor="start", fill=WARN)
    s += note(gx + wtot + 22, gy + 48, "count(o.id) 0, sum NULL", anchor="start", fill=WARN)
    s += verdict(vw, vh_, "PostgreSQL sorts NULL as if larger than every value, so in a descending sort the empty groups",
                 "come first. GROUP BY gave each country's NULLs one group, although NULL = NULL is not true.")
    return emit("07", "null-group-sorts-first", "NULLs sort first in a descending sort",
                "Twenty groups ranked by revenue: the five NULL groups take the top five places.",
                "where or having", vw, vh_, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    """NOT IN unrolled for customer 100,001, beside NOT EXISTS, after one NULL."""
    vw, vh_ = 1016, 520
    s = eyebrow(32, 40, "customer 100,001, after order 4242's customer_id became NULL")
    # NOT IN
    lx = 32
    s += txt(lx, 84, "id not in (select customer_id from orders)", size=12, weight="600",
             anchor="start", family=MONO)
    rows = [("order 1", "100001 <> 7920", "TRUE", INK),
            ("order 2", "100001 <> 15839", "TRUE", INK),
            ("⋯", "999,997 more comparisons", "TRUE", SOFT),
            ("order 4242", "100001 <> NULL", "UNKNOWN", WARN)]
    cols = [("order", 96), ("comparison", 210), ("result", 96)]
    s += grid_header(lx, 100, cols)
    for i, (o, cmp_, res, col) in enumerate(rows):
        y = 122 + i * 26
        s += grid_row(lx, y, cols, [o, cmp_, res], h=26, fill=WARN_TINT if col == WARN else "#ffffff",
                      colors={2: col, 1: col if col == WARN else INK})
    s += mono(lx, 254, "TRUE AND TRUE AND ⋯ AND UNKNOWN = UNKNOWN", size=10, fill=WARN, anchor="start",
              weight="600")
    s += note(lx, 274, "WHERE keeps only TRUE: customer 100,001 is dropped,", fill=WARN)
    s += note(lx, 288, "and so is every other customer", fill=WARN)
    s += box(lx, 312, 402, 60, fill=WARN_TINT, stroke=WARN)
    s += mono(lx + 14, 338, f"customers with no orders: {fmt(F['not_in'])} → {F['not_in_after_null']}",
              size=11, fill=WARN, anchor="start", weight="600")
    s += note(lx + 14, 358, "NOT IN, before and after the NULL")
    # NOT EXISTS
    rx = 540
    s += txt(rx, 84, "not exists (… where o.customer_id = c.id)", size=12, weight="600",
             anchor="start", family=MONO)
    s += box(rx, 100, 444, 128, fill="#ffffff", stroke=INK)
    s += mono(rx + 16, 126, "is there an order with customer_id = 100001?", size=10, fill=INK, anchor="start")
    s += note(rx + 16, 150, "1,000,000 orders checked; the NULL one is not a match,")
    s += note(rx + 16, 164, "because NULL = 100001 is UNKNOWN, not TRUE")
    s += mono(rx + 16, 192, "no match: NOT EXISTS is TRUE", size=10, fill=ACCENT, anchor="start", weight="600")
    s += note(rx + 16, 212, "customer 100,001 is kept", fill=ACCENT)
    s += box(rx, 312, 444, 60, fill=ACCENT_TINT, stroke=ACCENT)
    s += mono(rx + 14, 338, f"customers with no orders: {fmt(F['not_exists'])} → {fmt(F['not_exists_after_null'])}",
              size=11, fill=ACCENT, anchor="start", weight="600")
    s += note(rx + 14, 358, "NOT EXISTS, before and after the NULL")
    s += note(32, 404, "checked in the lab:  100001 not in (1, 2) is TRUE ·  100001 not in (1, 2, null) is NULL", fill=MUTED)
    s += verdict(vw, vh_, "NOT IN compares the customer with every value in the list, the NULL included.",
                 "NOT EXISTS only asks whether a matching row exists, and a NULL never matches.")
    return emit("08", "not-in-unknown", "Why one NULL empties NOT IN",
                "NOT IN unrolled into ANDed comparisons for one customer, beside NOT EXISTS.",
                "not in", vw, vh_, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    """Fan-out: a join repeats customer 1, EXISTS does not; two joins multiply."""
    vw, vh_ = 1016, 560
    s = eyebrow(32, 40, "where duplicate rows come from · the sample")
    # top: join vs exists for customer 1
    s += txt(32, 82, "customers with a paid order", size=13, weight="600", anchor="start")
    s += node(32, 100, 150, 50, "customer 1", "DE", kind="backend")
    cols = [("o.id", 56), ("amount", 72)]
    s += grid_header(232, 92, cols)
    s += grid_row(232, 114, cols, ["101", "5,000"], fill=ACCENT_TINT)
    s += grid_row(232, 136, cols, ["102", "3,000"], fill=ACCENT_TINT)
    s += hline(182, 232, 125)
    s += note(236, 172, "its two paid orders")
    # JOIN result
    jx = 470
    s += box(jx, 92, 240, 66, fill="#ffffff", stroke=INK)
    s += mono(jx + 14, 114, "JOIN", size=10, fill=INK, anchor="start", weight="600")
    s += mono(jx + 14, 134, "customer 1 · 101", size=9, fill=INK, anchor="start")
    s += mono(jx + 14, 150, "customer 1 · 102", size=9, fill=INK, anchor="start")
    s += note(jx + 236, 114, f"sample {S['join_paid']} · full {fmt(F['join_paid'])}", anchor="end")
    ex = 744
    s += box(ex, 92, 240, 66, fill=ACCENT_TINT, stroke=ACCENT)
    s += mono(ex + 14, 114, "EXISTS or IN", size=10, fill=ACCENT, anchor="start", weight="600")
    s += mono(ex + 14, 134, "customer 1", size=9, fill=INK, anchor="start")
    s += note(ex + 236, 114, f"sample {S['exists_paid']} · full {fmt(F['exists_paid'])}", anchor="end", fill=ACCENT)
    s += hline(360, jx, 125)
    s += f'<path d="M 360 125 H 420 Q 428 125 428 117 V 64 Q 428 56 436 56 H {ex + 120} Q {ex + 128} 56 {ex + 128} 64 V 92" fill="none" stroke="{MUTED}" stroke-width="1" marker-end="url(#arrow)"/>'
    s += masked(600, 60, "at most one row per customer", fill=ACCENT)
    s += masked(415, 140, "one row per match", anchor="middle")
    # bottom: the double join
    by = 236
    s += txt(32, by, "paid and refunded revenue, two joins to orders", size=13, weight="600", anchor="start")
    pcols = [("paid", 56), ("amt", 64)]
    rcols = [("refunded", 76), ("amt", 64)]
    s += node(32, by + 22, 150, 50, "customer 1", "2 paid · 1 refunded", kind="backend")
    s += grid_header(232, by + 14, pcols)
    s += grid_row(232, by + 36, pcols, ["101", "5,000"])
    s += grid_row(232, by + 58, pcols, ["102", "3,000"])
    s += grid_header(372, by + 14, rcols)
    s += grid_row(372, by + 36, rcols, ["103", "2,000"], fill=WARN_TINT, tcolor=WARN)
    s += note(232, by + 96, "2 paid × 1 refunded = 2 joined rows")
    ocols = [("paid", 56), ("refunded", 76)]
    ox = 600
    s += grid_header(ox, by + 14, ocols)
    s += grid_row(ox, by + 36, ocols, ["5,000", "2,000"], colors={1: WARN})
    s += grid_row(ox, by + 58, ocols, ["3,000", "2,000"], colors={1: WARN})
    s += hline(512, ox, by + 47)
    s += box(780, by + 14, 204, 66, fill=WARN_TINT, stroke=WARN)
    s += mono(794, by + 36, "refunded: 4,000", size=10, fill=WARN, anchor="start", weight="600")
    s += note(794, by + 54, "true total 2,000: counted twice", fill=WARN)
    s += note(794, by + 68, "paid: 8,000, correct here", fill=MUTED)
    s += hline(ox + 132, 780, by + 47)
    s += note(32, by + 130, "customer 4 has a paid order and no refunded one, so the inner join drops it:", fill=WARN)
    s += note(32, by + 144, "DE's paid total comes out 8,000 instead of 9,500", fill=WARN)
    s += box(32, by + 164, 952, 50, fill="#ffffff", stroke=MUTED)
    s += mono(48, by + 194, f"full shop: {fmt(F['query_a_rows_before_grouping'])} rows before grouping, from "
              f"1,000,000 orders · BR paid {fmt(F['query_a_broken'][0][1])} instead of "
              f"{fmt(F['query_a_fixed'][0][1])}", size=9.5, fill=INK, anchor="start", weight="500")
    s += verdict(vw, vh_, "A join repeats a row once per match, and two joins to the same table multiply. Every total",
                 "computed after them is inflated. EXISTS, IN, or one join with FILTERed sums avoid it.")
    return emit("09", "fan-out", "Where duplicate rows come from",
                "A join repeats a row once per match; EXISTS keeps it once; two joins multiply.",
                "duplicates", vw, vh_, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    """UNION ALL keeps all ten ids; UNION keeps the five distinct ones."""
    vw, vh_ = 1016, 430
    s = eyebrow(32, 40, "customer ids of paid orders, then of refunded orders · the sample")
    paid = [c for _, c, _, st in sorted(ORDERS) if st == "paid"]
    refunded = [c for _, c, _, st in sorted(ORDERS) if st == "refunded"]
    tw, gap = 34, 8
    s += note(32, 86, f"paid orders: {len(paid)} rows", fill=INK, weight="500")
    for i, c in enumerate(paid):
        s += tile(32 + i * (tw + gap), 96, str(c), fill=ACCENT_TINT if paid.count(c) > 1 else "#ffffff")
    s += note(32, 150, f"refunded orders: {len(refunded)} rows", fill=INK, weight="500")
    for i, c in enumerate(refunded):
        s += tile(32 + i * (tw + gap), 160, str(c))
    s += note(32, 210, "customer 1 is in the paid list twice,")
    s += note(32, 224, "and customers 1, 2, 3 and 5 are in both lists")
    # UNION ALL
    ux = 420
    allids = paid + refunded
    s += mono(ux, 86, f"UNION ALL · {len(allids)} rows", size=10, fill=INK, anchor="start", weight="600")
    for i, c in enumerate(allids):
        s += tile(ux + i * 26, 96, str(c), w=22, h=26)
    s += note(ux, 140, f"full shop: {fmt(F['paid_ids_rows'])} + {fmt(F['refunded_ids_rows'])} = {fmt(F['union_all'])} rows")
    # UNION
    s += mono(ux, 182, f"UNION · {S['union']} rows", size=10, fill=ACCENT, anchor="start", weight="600")
    for i, c in enumerate(sorted(set(allids))):
        s += tile(ux + i * 26, 192, str(c), w=22, h=26, fill=ACCENT_TINT, stroke=ACCENT, tcolor=ACCENT)
    s += note(ux, 236, f"full shop: {fmt(F['union'])} rows, one per customer", fill=ACCENT)
    s += note(ux, 250, f"the paid list UNIONed with itself: also {fmt(F['paid_union_itself'])}", fill=ACCENT)
    s += box(32, 286, 952, 52, fill="#ffffff", stroke=MUTED)
    s += mono(48, 310, f"after order 4242 lost its customer: UNION {fmt(F['union_after_null'])} rows, "
              f"the 100,000 ids and one NULL", size=10, fill=INK, anchor="start", weight="500")
    s += note(48, 328, "UNION treats two NULLs as equal, as DISTINCT does")
    s += verdict(vw, vh_, "UNION removes duplicates inside each input as well as across them. UNION ALL keeps every row.")
    return emit("10", "union-versus-union-all", "UNION against UNION ALL",
                "Ten ids in two lists: UNION ALL keeps all ten, UNION keeps five.",
                "duplicates", vw, vh_, s)


ALL = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06,
       "07": fig07, "08": fig08, "09": fig09, "10": fig10}

if __name__ == "__main__":
    for k in sys.argv[1:] or sorted(ALL):
        ALL[k]()
