#!/usr/bin/env python3
"""Build the finished social package for what-is-a-relational-database-postgresql.

Writes editable HTML sources for six shared feed cards (1080x1350) and four Story frames
(1080x1920) into assets/social/, with the Canery lockup taken unchanged from the locked
templates, and writes social.md beside blog.md from the same data, so the visible text,
alt text and transcripts cannot drift apart. SVG and PNG exports are produced afterwards by
the plugin's render_social.py. Every number comes from lab/captures.json.
"""
from __future__ import annotations

import html
import json
import pathlib
import re

ASSETS = pathlib.Path(__file__).resolve().parent
POST = ASSETS.parent
WORKSPACE = ASSETS.parents[3]
TEMPLATES = WORKSPACE / ".claude" / "blog-forge" / "skills" / "blog-visuals" / "assets"
SOCIAL = ASSETS / "social"
D = json.loads((POST / "lab" / "captures.json").read_text())
CANONICAL = "https://canery.in/blogs/what-is-a-relational-database-postgresql"

INK, MUTED, SOFT, ACCENT = "#2d3142", "#4f5d75", "#7a8399", "#eb6c36"
TINT, RULE, SILVER, SLATE = "rgba(235,108,54,0.10)", "rgba(45,49,66,.12)", "#bfc0c0", "#5e7a9b"
SERIF = "'Instrument Serif',Georgia,serif"
SANS = "'Geist',system-ui,sans-serif"
MONO = "'Geist Mono',ui-monospace,monospace"
FONT_LINK = ("https://fonts.googleapis.com/css2?family=Instrument+Serif&family=Geist:wght@400;500;600"
             "&family=Geist+Mono:wght@400;500;600&display=swap")


def e(s):
    return html.escape(str(s), quote=False)


def t(x, y, s, size, fill=INK, family=SANS, weight="400", anchor="start", track=None):
    tr = f' letter-spacing="{track}"' if track else ""
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}"{tr}>{e(s)}</text>')


def rect(x, y, w, h, fill="#fff", stroke=SILVER, rx=6, sw=1.2):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def fmt(n):
    return f"{n:,}"


def template_parts(kind):
    tpl = (TEMPLATES / f"social-{kind}-template.html").read_text(encoding="utf-8")
    definition = re.search(rf'<g id="canery-lockup-{kind}"[\s\S]*?</g>', tpl).group(0)
    marker = re.search(r'<g data-canery-logo="lockup"[^>]*>[\s\S]*?</g>', tpl).group(0)
    return definition, marker


# ------------------------------------------------------------------ shared numbers
REV = {c: (int(r), int(n)) for c, r, n in D["revenue_clean"]}
JP, JP_N = REV["JP"]
DUP = D["dup_amount"]
COST_A = D["cost_plan_chosen"]["total_cost"]
COST_B = D["cost_plan_runner_up"]["total_cost"]
RATIO = COST_B / COST_A
EST, ACT = 140514, 111111          # per process, from the shipped EXPLAIN ANALYZE text (L41)
PLAN_EST = f"estimated {fmt(EST)} paid orders per process; each found {fmt(ACT)}"
CAT_LABEL = "pg_class · four of its rows"
FOOT = "POSTGRESQL FOUNDATIONS · PART 4 · CANERY.IN"


def arrow_down(x, y1, y2, label=None, big=False):
    s = (f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2 - 10}" stroke="{MUTED}" stroke-width="2"/>'
         f'<polygon points="{x - 8},{y2 - 12} {x + 8},{y2 - 12} {x},{y2}" fill="{MUTED}"/>')
    if label:
        s += t(x + 18, (y1 + y2) / 2 + 6, label, 17 if not big else 20, SOFT, MONO, "500")
    return s


# ------------------------------------------------------------------ artefacts (panel content)
STAGES = [("parser", "checks the grammar, then looks up every name"),
          ("rewriter", "replaces each view with its definition"),
          ("planner", "estimates every path, keeps the cheapest"),
          ("executor", "walks the plan tree and returns rows")]
STAGE_EDGES = ["query tree", "rewritten query tree", "plan tree"]


def art_stages(x, y, w, h, big=False):
    s = ""
    bw, bh = 640, (92 if not big else 104)
    bx = x + (w - bw) / 2
    step = (h - 150) / 4
    s += t(x + w / 2, y + 44, "your SQL query", 20 if not big else 23, MUTED, MONO, "500", "middle")
    ys = [y + 70 + i * step for i in range(4)]
    s += arrow_down(x + w / 2, y + 54, ys[0])
    for i, ((name, what), yy) in enumerate(zip(STAGES, ys)):
        focal = name == "planner"
        s += rect(bx, yy, bw, bh, TINT if focal else "#fff", ACCENT if focal else INK, 8, 2 if focal else 1.4)
        s += t(bx + 28, yy + bh / 2 - 4, name, 28 if not big else 32, ACCENT if focal else INK, SANS, "600")
        s += t(bx + 28, yy + bh / 2 + 28, what, 18 if not big else 21, MUTED, SANS)
        if i < 3:
            s += arrow_down(x + w / 2, yy + bh, ys[i + 1], STAGE_EDGES[i], big)
    yo = ys[-1] + bh
    s += arrow_down(x + w / 2, yo, yo + 44)
    s += t(x + w / 2, yo + 70, "5 rows: revenue per country", 20 if not big else 23, INK, MONO, "600", "middle")
    return s


DUP_ROWS = ["4242", "92399", fmt(DUP), "paid"]


def art_duplicate(x, y, w, h, big=False):
    s = ""
    cols = [("id", 150), ("customer_id", 230), ("amount_cents", 250), ("status", 150)]
    gx = x + (w - sum(c for _, c in cols)) / 2
    gy = y + 60
    s += t(gx, gy - 18, "orders · no primary key", 18 if not big else 21, SOFT, MONO, "500")
    cx = gx
    for name, cw in cols:
        s += rect(cx, gy, cw, 46, "rgba(45,49,66,.06)", SILVER, 0, 1)
        s += t(cx + cw / 2, gy + 30, name, 18 if not big else 20, INK, MONO, "600", "middle")
        cx += cw
    for r in range(2):
        cx, yy = gx, gy + 46 + r * 58
        for (name, cw), v in zip(cols, DUP_ROWS):
            s += rect(cx, yy, cw, 58, TINT, ACCENT, 0, 1.2)
            s += t(cx + cw / 2, yy + 37, v, 24 if not big else 27, INK, MONO, "500", "middle")
            cx += cw
    s += t(gx, gy + 46 + 2 * 58 + 34, "the same row, twice: accepted without a warning", 18 if not big else 21, ACCENT, MONO, "500")
    yb = gy + 260 + (40 if big else 0)
    s += t(x + 64, yb, "revenue for JP", 20 if not big else 23, MUTED, SANS)
    s += t(x + 64, yb + 62, f"{fmt(JP)}", 44 if not big else 50, SOFT, MONO, "500")
    s += t(x + w - 64, yb + 58, "before", 20 if not big else 23, SOFT, SANS, "500", "end")
    s += t(x + 64, yb + 126, f"{fmt(JP + DUP)}", 44 if not big else 50, ACCENT, MONO, "600")
    s += t(x + w - 64, yb + 122, "after the copy", 20 if not big else 23, ACCENT, SANS, "600", "end")
    s += t(x + 64, yb + 172, f"+{fmt(DUP)} cents · +1 paid order · same query", 20 if not big else 23, INK, SANS, "600")
    return s


FIX_STEPS = [
    ("alter table orders add primary key (id);", "refused while the copy exists",
     'could not create unique index "orders_pkey"', False),
    ("delete one copy, then add the key again", "accepted", None, True),
    ("insert the copy again", "refused, for every program that connects",
     'duplicate key value violates unique constraint "orders_pkey"', False),
]


def art_fix(x, y, w, h, big=False):
    s = ""
    step = (h - 60) / 3
    for i, (cmd, verdict, msg, ok) in enumerate(FIX_STEPS):
        yy = y + 40 + i * step
        c = "#5e7a6f" if ok else ACCENT
        s += f'<circle cx="{x + 64}" cy="{yy + 22}" r="17" fill="none" stroke="{c}" stroke-width="2.5"/>'
        s += t(x + 64, yy + 30, str(i + 1), 18, c, MONO, "600", "middle")
        s += t(x + 104, yy + 30, cmd, 20 if not big else 23, INK, MONO, "600")
        s += t(x + 104, yy + 66, verdict, 20 if not big else 23, c, SANS, "600")
        if msg:
            s += t(x + 104, yy + 100, msg, 16 if not big else 18, MUTED, MONO)
    return s


def art_plan(x, y, w, h, big=False):
    s = ""
    bx, bwmax = x + 64, w - 128
    k = bwmax / COST_B
    rows = [("hash join plan · chosen", COST_A, ACCENT, TINT), ("next-best plan · hash joins off", COST_B, "#5e7a9b", "rgba(94,122,155,.22)")]
    for i, (lab, cst, stroke, fill) in enumerate(rows):
        yy = y + 70 + i * (150 if not big else 170)
        s += t(bx, yy, lab, 20 if not big else 23, INK, SANS, "600")
        s += f'<rect x="{bx}" y="{yy + 18}" width="{cst * k}" height="56" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>'
        s += t(bx + 16, yy + 56, f"cost {cst:,.2f}", 22 if not big else 25, INK, MONO, "600")
    yr = y + 400 + (40 if big else 0)
    s += t(bx, yr, f"{RATIO:.2f}× the estimated cost", 28 if not big else 32, ACCENT, SANS, "600")
    s += t(bx, yr + 56, PLAN_EST, 19 if not big else 22, MUTED, SANS)
    s += t(bx, yr + 92, "units are arbitrary: compare plans, never clocks", 19 if not big else 22, MUTED, SANS)
    return s


def art_null(x, y, w, h, big=False):
    s = ""
    bx = x + 64
    for i, (lab, val, sub, hot) in enumerate([
            ("count(*)", D["count_star"], "counts rows", False),
            ("count(amount_cents)", D["count_amount"], "counts values that are not NULL", True)]):
        yy = y + 50 + i * (150 if not big else 170)
        s += rect(bx, yy, w - 128, 120, TINT if hot else "#fff", ACCENT if hot else INK, 8, 1.6)
        s += t(bx + 28, yy + 50, lab, 24 if not big else 27, ACCENT if hot else INK, MONO, "600")
        s += t(bx + w - 156, yy + 56, fmt(val), 44 if not big else 50, ACCENT if hot else INK, MONO, "600", "end")
        s += t(bx + 28, yy + 92, sub, 18 if not big else 21, MUTED, SANS)
    yw = y + 400 + (60 if big else 0)
    s += t(bx, yw, "where amount_cents = null", 22 if not big else 25, INK, MONO, "500")
    s += t(x + w - 64, yw, f"{D['eq_null_rows']} rows", 22 if not big else 25, INK, MONO, "600", "end")
    s += t(bx, yw + 52, "where amount_cents is null", 22 if not big else 25, INK, MONO, "500")
    s += t(x + w - 64, yw + 52, f"{D['is_null_rows']} row", 22 if not big else 25, ACCENT, MONO, "600", "end")
    s += t(bx, yw + 110, "a comparison with NULL is unknown, and WHERE keeps only true", 18 if not big else 21, MUTED, SANS)
    return s


CAT_ROWS = [("customers", "r", "3"), ("orders", "r", "5"), ("pg_attribute", "r", "25"), ("pg_class", "r", "34")]


def art_catalog(x, y, w, h, big=False):
    s = ""
    cols = [("relname", 300), ("relkind", 170), ("relnatts", 190)]
    gx = x + (w - sum(c for _, c in cols)) / 2
    gy = y + 70
    s += t(gx, gy - 20, CAT_LABEL, 17 if not big else 19, SOFT, MONO, "500")
    cx = gx
    for name, cw in cols:
        s += rect(cx, gy, cw, 52, "rgba(45,49,66,.06)", SILVER, 0, 1)
        s += t(cx + cw / 2, gy + 34, name, 20 if not big else 22, INK, MONO, "600", "middle")
        cx += cw
    for r, vals in enumerate(CAT_ROWS):
        cx, yy = gx, gy + 52 + r * 64
        hot = vals[0] == "pg_class"
        for (name, cw), v in zip(cols, vals):
            s += rect(cx, yy, cw, 64, TINT if hot else "#fff", ACCENT if hot else SILVER, 0, 1.2)
            s += t(cx + cw / 2, yy + 41, v, 24 if not big else 27, ACCENT if hot else INK, MONO, "500", "middle")
            cx += cw
    s += t(gx, gy + 52 + 4 * 64 + 56, "pg_class is a table, so it has a row in pg_class", 20 if not big else 23, ACCENT, SANS, "600")
    s += t(gx, gy + 52 + 4 * 64 + 96, "every table, column and constraint is a row you can query", 18 if not big else 21, MUTED, SANS)
    return s


# ------------------------------------------------------------------ cards
def tr(*parts):
    return " · ".join(p for p in parts if p)


T_STAGES = tr("your SQL query", *[f"{n} {w}" for n, w in STAGES], *STAGE_EDGES, "5 rows: revenue per country")
T_DUP = tr("orders · no primary key", "id", "customer_id", "amount_cents", "status", *DUP_ROWS, *DUP_ROWS,
           "the same row, twice: accepted without a warning", "revenue for JP", fmt(JP), "before",
           fmt(JP + DUP), "after the copy",
           f"+{fmt(DUP)} cents · +1 paid order · same query")
T_FIX = tr(*[tr(f"{i}", c, v, m) for i, (c, v, m, _) in enumerate(FIX_STEPS, 1)])
T_PLAN = tr("hash join plan · chosen", f"cost {COST_A:,.2f}", "next-best plan · hash joins off", f"cost {COST_B:,.2f}",
            f"{RATIO:.2f}× the estimated cost", PLAN_EST,
            "units are arbitrary: compare plans, never clocks")
T_NULL = tr("count(*)", fmt(D["count_star"]), "counts rows", "count(amount_cents)", fmt(D["count_amount"]),
            "counts values that are not NULL", "where amount_cents = null", f"{D['eq_null_rows']} rows",
            "where amount_cents is null", f"{D['is_null_rows']} row", "a comparison with NULL is unknown, and WHERE keeps only true")
T_CAT = tr(CAT_LABEL, "relname", "relkind", "relnatts",
           *[tr(*r) for r in CAT_ROWS], "pg_class is a table, so it has a row in pg_class",
           "every table, column and constraint is a row you can query")

KW = "PostgreSQL, relational database, SQL"
FEED = [
    dict(stem="feed-01-what-and-how", title="You say what. It decides how.", role="cover",
         setup="Four stages stand between your query and its rows.",
         take="Your query never names an index, an order or a path.", art=art_stages,
         beat="A relational database separates what you ask for from how it is fetched, in four visible stages.",
         source="Intuition; What happens between the query and the rows?; Figure 4; ledger L12, L05",
         structure="Headline and setup; a vertical flow from the SQL query through four stage boxes (planner highlighted), each edge labelled with what it carries, to five result rows; takeaway and footer.",
         transcript=tr("You say what. It decides how.", "Four stages stand between your query and its rows.", T_STAGES,
                       "Your query never names an index, an order or a path.", FOOT),
         alt="A SQL query passing through PostgreSQL's four stages, parser, rewriter, planner and executor, to five result rows.",
         longdesc="Cover card. A vertical flow: the SQL query enters the parser, which checks the grammar and then looks up every name; a query tree goes to the rewriter, which replaces views with their definitions; the rewritten query tree goes to the planner, highlighted, which estimates every path and keeps the cheapest; the plan tree goes to the executor, which returns five rows of revenue per country. The query itself never says which index, order or path to use.",
         keywords=KW + ", query planner, parser, executor"),
    dict(stem="feed-02-duplicate", title="One duplicate, no error", role="technical",
         setup="orders has no primary key, so an exact copy of order 4242 went in.",
         take="A table is a set only once you declare a key.", art=art_duplicate,
         beat="Without a primary key, PostgreSQL stores an exact duplicate and the revenue total silently moves.",
         source="Surprise one: the table accepted a duplicate; Figure 6; ledger L38, L47",
         structure="Headline and setup; the duplicated order row drawn twice under its column names; revenue for JP before and after, the difference called out; takeaway and footer.",
         transcript=tr("One duplicate, no error", "orders has no primary key, so an exact copy of order 4242 went in.", T_DUP,
                       "A table is a set only once you declare a key.", FOOT),
         alt=f"Order 4242 stored twice in a table with no key, raising revenue for JP from {fmt(JP)} to {fmt(JP + DUP)} cents.",
         longdesc=f"The orders table has no primary key, so inserting an exact copy of order 4242 (customer 92399, {fmt(DUP)} cents, paid) succeeds without a warning. Both copies join to the same customer, so the revenue for JP rises from {fmt(JP)} to {fmt(JP + DUP)} cents, exactly {fmt(DUP)} more, with one more paid order. The query is unchanged and nothing errors. PostgreSQL 18.6, lab measurement.",
         keywords=KW + ", primary key, duplicate rows, data integrity"),
    dict(stem="feed-03-the-fix", title="The key that stops it", role="technical",
         setup="The constraint cannot go on while the copy is there.",
         take="A constraint binds every program; an app check binds one.", art=art_fix,
         beat="Declaring the primary key fails until the duplicate is removed, then refuses the copy for good.",
         source="Surprise one: the table accepted a duplicate; ledger L39, L23",
         structure="Headline and setup; three numbered steps with the statement, the verdict and the server's message; takeaway and footer.",
         transcript=tr("The key that stops it", "The constraint cannot go on while the copy is there.", T_FIX,
                       "A constraint binds every program; an app check binds one.", FOOT),
         alt="Three steps: adding the primary key is refused while the duplicate exists, accepted after deleting it, then refuses the copy.",
         longdesc='Step 1: alter table orders add primary key (id) fails with could not create unique index "orders_pkey", because order 4242 is duplicated. Step 2: after one copy is deleted, the same statement succeeds. Step 3: inserting the copy again is refused with duplicate key value violates unique constraint "orders_pkey", for every program that connects. PostgreSQL 18.6, lab measurement.',
         keywords=KW + ", primary key, constraint, unique index"),
    dict(stem="feed-04-cheapest-plan", title="The planner picks the cheapest", role="technical",
         setup="It estimated the cost of each way to answer the question.",
         take="Estimates decide how a query runs, never what it returns.", art=art_plan,
         beat="The planner chose a hash join over a plan it estimated at 2.27 times the cost, despite a wrong row estimate.",
         source="Stage 3 and Stage 4; Figure 1; ledger L36, L41, L17",
         structure="Headline and setup; two proportional cost bars, chosen and next-best; the cost ratio; the per-process estimate against the actual count; takeaway and footer.",
         transcript=tr("The planner picks the cheapest", "It estimated the cost of each way to answer the question.", T_PLAN,
                       "Estimates decide how a query runs, never what it returns.", FOOT),
         alt=f"Two cost bars: the chosen hash join plan at {COST_A:,.2f} and the next-best plan at {COST_B:,.2f}, {RATIO:.2f} times the cost.",
         longdesc=f"For the revenue query, the planner's chosen plan, a hash join, has an estimated cost of {COST_A:,.2f}. With hash joins turned off, the next-best plan costs {COST_B:,.2f}, {RATIO:.2f} times as much. The planner estimated {fmt(EST)} paid orders per process; each process found {fmt(ACT)}. Cost units are arbitrary, so they compare plans with each other, not with a clock. PostgreSQL 18.6, lab measurement.",
         keywords=KW + ", query planner, EXPLAIN, hash join, cost estimate"),
    dict(stem="feed-05-null", title="NULL is not a value", role="technical",
         setup="Blank one amount, and two counts that look alike disagree.",
         take="count(*) counts rows. count(column) counts values.", art=art_null,
         beat="One NULL makes count(*) and count(column) differ and makes = NULL match nothing.",
         source="Surprise two: NULL is not a value; Figure 7; ledger L19, L40, L49, L50",
         structure="Headline and setup; two count boxes with their values; two WHERE clauses with the rows each matches; a one-line reason; takeaway and footer.",
         transcript=tr("NULL is not a value", "Blank one amount, and two counts that look alike disagree.", T_NULL,
                       "count(*) counts rows. count(column) counts values.", FOOT),
         alt=f"count(*) returns {fmt(D['count_star'])} and count(amount_cents) {fmt(D['count_amount'])}; = null matches 0 rows and is null matches 1.",
         longdesc=f"After one order's amount is set to NULL, count(*) returns {fmt(D['count_star'])} because it counts rows, while count(amount_cents) returns {fmt(D['count_amount'])} because it counts only non-NULL values. where amount_cents = null matches 0 rows, because a comparison with NULL is unknown and WHERE keeps only rows whose condition is true; where amount_cents is null matches 1. PostgreSQL 18.6, lab measurement.",
         keywords=KW + ", NULL, three-valued logic, count, aggregate"),
    dict(stem="feed-06-read-the-post", title="Even the catalog is a table", role="cta",
         setup="PostgreSQL stores its schema as rows, including its own.",
         take="Read the full post on canery.in →", art=art_catalog,
         beat="The schema is data: pg_class has a row for every table, pg_class included.",
         source="The schema is stored as data; Figure 3; ledger L21, L32",
         structure="Headline and setup; four rows of pg_class with their kind and column count, pg_class's own row highlighted; call to action and footer.",
         transcript=tr("Even the catalog is a table", "PostgreSQL stores its schema as rows, including its own.", T_CAT,
                       "Read the full post on canery.in →", FOOT),
         alt="The pg_class catalog listing customers, orders, pg_attribute and pg_class itself, with 3, 5, 25 and 34 columns.",
         longdesc="Closing card. Four rows of the pg_class catalog: customers (3 columns), orders (5), pg_attribute (25) and pg_class itself (34), all ordinary tables of kind r. The catalog describes itself in the same form it describes your tables. Call to action: read the full post on canery.in.",
         keywords=KW + ", system catalog, pg_class, schema"),
]

STORY = [
    dict(stem="story-01-what-and-how", title="You say what. It decides how.", role="cover",
         setup="Four stages between your query and its rows.", take="Watch each one in the post.", art=art_stages,
         overlay="What a relational database actually does",
         beat="Story opener: the four stages a query passes through.", source=FEED[0]["source"],
         structure="Hook headline, setup line, a tall panel with the four stage boxes and labelled edges, takeaway, footer.",
         transcript=tr("You say what. It decides how.", "Four stages between your query and its rows.", T_STAGES,
                       "Watch each one in the post.", FOOT),
         alt="Story cover: a SQL query passing through the parser, rewriter, planner and executor to five result rows.",
         longdesc="Story cover, recomposed for 9:16. The SQL query flows through four stage boxes: the parser (grammar, then names), the rewriter (views replaced), the planner (highlighted; cheapest estimated path) and the executor (walks the plan tree), ending in five rows of revenue per country.",
         keywords=FEED[0]["keywords"]),
    dict(stem="story-02-duplicate", title="One duplicate, no error", role="technical",
         setup="No primary key, so the copy went in.", take="Declare the key before the incident.", art=art_duplicate,
         overlay=f"One copied row moved revenue by {fmt(DUP)} cents",
         beat="Story beat: a duplicate row silently moved a revenue total.", source=FEED[1]["source"], structure=FEED[1]["structure"],
         transcript=tr("One duplicate, no error", "No primary key, so the copy went in.", T_DUP,
                       "Declare the key before the incident.", FOOT),
         alt=f"Story frame: the same order row stored twice, and revenue for JP rising from {fmt(JP)} to {fmt(JP + DUP)} cents.",
         longdesc=f"Story frame, recomposed for 9:16. The orders table has no primary key, so order 4242 (customer 92399, {fmt(DUP)} cents, paid) appears twice, identical in every column. Revenue for JP is shown before ({fmt(JP)} cents) and after the copy ({fmt(JP + DUP)} cents): {fmt(DUP)} cents and one paid order more, with the same query and no error. The takeaway: declare the key before the incident.",
         keywords=FEED[1]["keywords"]),
    dict(stem="story-03-null", title="NULL is not a value", role="technical",
         setup="Two counts that look alike disagree.", take="count(column) skips the unknown.", art=art_null,
         overlay="Why count(*) and count(column) disagree",
         beat="Story beat: one NULL splits two counts and hides its row from = NULL.", source=FEED[4]["source"], structure=FEED[4]["structure"],
         transcript=tr("NULL is not a value", "Two counts that look alike disagree.", T_NULL,
                       "count(column) skips the unknown.", FOOT),
         alt=f"Story frame: count(*) at {fmt(D['count_star'])} against count(amount_cents) at {fmt(D['count_amount'])}, and = null matching no rows.",
         longdesc=f"Story frame, recomposed for 9:16. With one amount set to NULL, count(*) returns {fmt(D['count_star'])} because it counts rows, and count(amount_cents) returns {fmt(D['count_amount'])} because it counts only values that are not NULL. where amount_cents = null matches 0 rows and where amount_cents is null matches 1, because a comparison with NULL is unknown and WHERE keeps only rows whose condition is true.",
         keywords=FEED[4]["keywords"]),
    dict(stem="story-04-read-the-post", title="The key that stops it", role="cta",
         setup="Declared once, enforced for every program.", take="Read how → canery.in", art=art_fix,
         overlay="Read how →",
         beat="Story close: the constraint that would have stopped the duplicate, and the call to action.", source=FEED[2]["source"], structure=FEED[2]["structure"],
         transcript=tr("The key that stops it", "Declared once, enforced for every program.", T_FIX,
                       "Read how → canery.in", FOOT),
         alt="Closing story frame: the primary key refused while the duplicate exists, accepted once it is gone, then refusing the copy.",
         longdesc='Closing story frame, recomposed for 9:16, with the call to action. Step 1: alter table orders add primary key (id) is refused with could not create unique index "orders_pkey" while order 4242 is duplicated. Step 2: after one copy is deleted, the key is accepted. Step 3: inserting the copy again is refused with duplicate key value violates unique constraint "orders_pkey", for every program that connects. Call to action: read how on canery.in.',
         keywords=FEED[2]["keywords"]),
]


def wrap(title, desc, kind, index, total, card):
    definition, marker = template_parts(kind)
    W, H = (1080, 1350) if kind == "feed" else (1080, 1920)
    feed = kind == "feed"
    cy = 105 if feed else 285
    hy = 258 if feed else 470
    sy = 316 if feed else 535
    py, ph = (390, 690) if feed else (650, 760)
    ly, ty, fy = (1174, 1228, 1295) if feed else (1510, 1580, 1655)
    last = index == total
    body = [
        f'<rect width="{W}" height="{H}" fill="#f5f5f5"/>', marker,
        t(1008, cy, f"{index:02d} / {total:02d}", 15 if feed else 17, ACCENT if last else SOFT, MONO, "500", "end", ".16em"),
        f'<line x1="72" y1="{cy + 45 if feed else 340}" x2="1008" y2="{cy + 45 if feed else 340}" stroke="{RULE}"/>',
        t(72, hy, card["title"], 64 if feed else 72, INK, SERIF),
        t(72, sy, card["setup"], 22 if feed else 26, MUTED, SANS),
        rect(72, py, 936, ph, "#fff", SILVER, 8),
        card["art"](72, py, 936, ph, big=not feed),
        f'<line x1="72" y1="{ly}" x2="1008" y2="{ly}" stroke="{RULE}"/>',
        t(72, ty, card["take"], 24 if feed else 28, ACCENT if last else INK, SANS, "600"),
        t(72, fy, "POSTGRESQL FOUNDATIONS · PART 4 · CANERY.IN", 14 if feed else 16, ACCENT, MONO, "500", track=".14em"),
    ]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img">'
           f"<title>{e(title)}</title><desc>{e(desc)}</desc><defs>{definition}</defs>" + "".join(body) + "</svg>")
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            f"<title>{e(title)}</title><link href=\"{FONT_LINK}\" rel=\"stylesheet\">"
            "<style>html,body{margin:0;background:#f5f5f5}svg{display:block}</style>"
            f"</head><body>{svg}</body></html>\n")


def meta_block(card, kind):
    plat = "Instagram feed, LinkedIn" if kind == "feed" else "Instagram Story"
    dim = "1080×1350" if kind == "feed" else "1080×1920"
    return "\n".join([
        f"### {card['stem']}", "",
        f"- File: `assets/social/{card['stem']}.png`",
        f"- Title: {card['title']}",
        f"- Platforms: {plat}",
        f"- Role: {card['role']}",
        f"- Dimensions: {dim}",
        f"- Narrative beat: {card['beat']}",
        f"- Technical source: {card['source']}",
        f"- Visual structure: {card['structure']}",
        f"- Visible-text transcript: {card['transcript']}",
        f"- Alt text: {card['alt']}",
        f"- Long description: {card['longdesc']}",
        f"- Keywords: {card['keywords']}",
        f"- Canonical URL: {CANONICAL}", ""])


def build():
    SOCIAL.mkdir(exist_ok=True)
    for i, c in enumerate(FEED, 1):
        (SOCIAL / f"{c['stem']}.html").write_text(wrap(c["title"], c["alt"], "feed", i, len(FEED), c), encoding="utf-8")
    for i, c in enumerate(STORY, 1):
        (SOCIAL / f"{c['stem']}.html").write_text(wrap(c["title"], c["alt"], "story", i, len(STORY), c), encoding="utf-8")
    feed_order = "\n".join(f"{i}. `assets/social/{c['stem']}.png` — {c['beat']}" for i, c in enumerate(FEED, 1))
    story_order = "\n".join(f"{i}. `assets/social/{c['stem']}.png` — Overlay: {c['overlay']}" for i, c in enumerate(STORY, 1))
    md = f"""---
social_schema: 2
canonical_url: "{CANONICAL}"
---

# Social publishing package — what-is-a-relational-database-postgresql

## LinkedIn post

What does a relational database actually do between your query and its rows? I ran one business question on PostgreSQL 18 and watched.

You write what you want: revenue per country for paid orders. The server decides how, in four stages: the parser checks the grammar and then the names, the rewriter expands views, the planner estimates each path and keeps the cheapest, and the executor runs it. Its estimate for the next-best plan was {RATIO:.2f} times the cost of the one it picked.

Then two surprises on the same tables. The orders table had no primary key, so an exact copy of one order went in without a warning and moved one country's revenue by {fmt(DUP)} cents. And after one amount was set to NULL, count(*) said {fmt(D['count_star'])} while count(amount_cents) said {fmt(D['count_amount'])}.

Part 4 of PostgreSQL Foundations, the first written for someone who has never used a database. Swipe through the six cards; the link is in the first comment.

## LinkedIn first comment

A table is a set of rows only once you declare a key, and NULL is a marker for unknown, not a value. Both rules are cheap to learn and expensive to learn late.

Read the full article on Canery: {CANONICAL}

## Instagram caption

What a relational database actually does: you say what, it decides how, in four stages you can watch. Plus two silent bugs on real rows: a duplicate order that moved revenue by {fmt(DUP)} cents, and a NULL that made count(*) and count(amount_cents) disagree. Part 4 of PostgreSQL Foundations. Full article on canery.in, link in bio.

## Shared feed order

{{feed_order}}

## Instagram Story

- CTA: Read what PostgreSQL does between your query and its rows
- Link sticker label: Read the article
- Link sticker URL: {CANONICAL}

### Story order

{{story_order}}

## Asset metadata

""".replace("{feed_order}", feed_order).replace("{story_order}", story_order) + "\n".join(meta_block(c, "feed") for c in FEED) + "\n" + "\n".join(meta_block(c, "story") for c in STORY)
    (POST / "social.md").write_text(md, encoding="utf-8")
    print(f"  social: {len(FEED)} feed + {len(STORY)} story sources, social.md")


if __name__ == "__main__":
    build()
