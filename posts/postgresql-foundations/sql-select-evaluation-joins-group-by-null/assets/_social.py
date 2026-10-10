#!/usr/bin/env python3
"""Build the finished social package for sql-select-evaluation-joins-group-by-null.

Copied from part 4 so the series' cards read as one set. Writes editable HTML sources for six
shared feed cards (1080x1350) and four Story frames
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
CANONICAL = "https://canery.in/blogs/sql-select-evaluation-joins-group-by-null"

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
F = D["full"]
WARN, WARN_TINT = "#b5452a", "rgba(181,69,42,0.08)"
FOOT = "POSTGRESQL FOUNDATIONS · PART 5 · CANERY.IN"
REPORT = F["report_ordered"]
SECOND = F["second_row_by_plan"]
TIES = [r[0] for r in F["with_ties"]]
NULL_GROUPS = F["status_report_top5"]
NULLS_LAST = F["status_report_nulls_last"]
TIED5 = F["status_report_with_ties"][-1]


def hline(x1, x2, y, stroke=RULE, sw=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


# ------------------------------------------------------------------ artefacts (panel content)
ORDER = [("FROM · JOIN", "2nd", fmt(F["inner_join"])),
         ("WHERE", "3rd", fmt(F["where_paid"])),
         ("GROUP BY", "4th", f"{F['groups']} groups"),
         ("HAVING", "5th", f"{F['groups']}"),
         ("SELECT", "1st", f"{F['groups']}"),
         ("DISTINCT", "with SELECT", f"{F['groups']}"),
         ("ORDER BY", "6th", f"{F['groups']}, sorted"),
         ("LIMIT 2", "7th", "2")]


def art_order(x, y, w, h, big=False):
    s = ""
    step = (h - 104) / 8
    s += t(x + 40, y + 46, "evaluated", 17 if not big else 19, SOFT, MONO, "500")
    s += t(x + 470, y + 46, "written", 17 if not big else 19, SOFT, MONO, "500")
    s += t(x + w - 40, y + 46, "rows after it", 17 if not big else 19, SOFT, MONO, "500", "end")
    for i, (name, written, rows) in enumerate(ORDER):
        yy = y + 70 + i * step
        hot = name == "SELECT"
        if hot:
            s += rect(x + 20, yy + 4, w - 40, step - 8, TINT, ACCENT, 6, 1.6)
        elif i:
            s += hline(x + 40, x + w - 40, yy)
        c = ACCENT if hot else INK
        s += t(x + 40, yy + step / 2 + 9, f"{i + 1}  {name}", 26 if not big else 29, c, SANS, "600")
        s += t(x + 470, yy + step / 2 + 8, written, 19 if not big else 22, ACCENT if hot else MUTED, MONO, "500")
        s += t(x + w - 40, yy + step / 2 + 9, rows, 24 if not big else 27, c, MONO, "600", "end")
    return s


def art_tie(x, y, w, h, big=False):
    s = ""
    rh = 52 if not big else 60
    s += t(x + 40, y + 50, "order by revenue_cents desc limit 2", 18 if not big else 21, SOFT, MONO, "500")
    for i, (c, n, rev) in enumerate(REPORT):
        yy = y + 72 + i * rh
        hot = c in ("IN", "JP")
        if hot:
            s += f'<rect x="{x + 20}" y="{yy}" width="{w - 40}" height="{rh}" fill="{TINT}"/>'
        rank = "1" if i == 0 else ("2 or 3" if hot else str(i + 1))
        col = ACCENT if hot else INK
        s += t(x + 40, yy + rh / 2 + 8, rank, 22 if not big else 25, col, MONO, "500")
        s += t(x + 260, yy + rh / 2 + 8, c, 24 if not big else 27, col, MONO, "600")
        s += t(x + w - 40, yy + rh / 2 + 8, fmt(rev), 24 if not big else 27, col, MONO, "600", "end")
    ly = y + 72 + 2 * rh
    s += hline(x + 20, x + w - 20, ly, WARN, 2.5, "10,7")
    s += f'<rect x="{x + 352}" y="{ly - 15}" width="118" height="30" fill="#fff"/>'
    s += t(x + 411, ly + 7, "LIMIT 2", 18 if not big else 20, WARN, MONO, "600", "middle")
    oy = y + 72 + 5 * rh + (54 if not big else 70)
    outs = [("default settings", f"DE, {SECOND['default']}", INK),
            ("parallel workers off", f"DE, {SECOND['max_parallel_workers_per_gather = 0']}", INK),
            ("fetch first 2 rows with ties", ", ".join(TIES), ACCENT)]
    for i, (lab, got, col) in enumerate(outs):
        yy = oy + i * (54 if not big else 64)
        s += t(x + 40, yy, lab, 21 if not big else 24, MUTED, SANS)
        s += t(x + w - 40, yy, got, 24 if not big else 27, col, MONO, "600", "end")
    return s


JOINS = [("customers join orders", fmt(F["inner_join"]), "every order has a customer", INK, "#fff"),
         ("customers left join orders", fmt(F["left_join"]), f"+{fmt(F['padded_rows'])} padded rows, one per customer with no orders", INK, "#fff"),
         ("left join … where o.status = 'paid'", fmt(F["left_join_where_paid"]), "padded rows dropped: NULL = 'paid' is unknown", WARN, WARN_TINT),
         ("left join … on … and o.status = 'paid'", fmt(F["left_join_on_paid"]), "padded rows kept: the condition only decides the match", ACCENT, TINT)]


def art_leftjoin(x, y, w, h, big=False):
    s = ""
    bh, gap = (128, 22) if not big else (150, 30)
    y0 = y + (h - 4 * bh - 3 * gap) / 2
    for i, (q, n, sub, col, fill) in enumerate(JOINS):
        yy = y0 + i * (bh + gap)
        s += rect(x + 32, yy, w - 64, bh, fill, col if col != INK else SILVER, 8, 1.6)
        s += t(x + 60, yy + 46, q, 21 if not big else 24, INK, MONO, "500")
        s += t(x + w - 60, yy + 50, n, 34 if not big else 38, col, MONO, "600", "end")
        s += t(x + 60, yy + bh - 30, sub, 18 if not big else 21, col if col != INK else MUTED, SANS)
    return s


def art_nullsort(x, y, w, h, big=False):
    s = ""
    rh = 40 if not big else 44
    s += t(x + 40, y + 52, "order by revenue_cents desc limit 5", 18 if not big else 21, WARN, MONO, "500")
    for i, (c, st, n, rev) in enumerate(NULL_GROUPS):
        yy = y + 70 + i * rh
        s += f'<rect x="{x + 20}" y="{yy}" width="{w - 40}" height="{rh - 4}" fill="{WARN_TINT}"/>'
        s += t(x + 40, yy + rh / 2 + 6, c, 21 if not big else 24, WARN, MONO, "600")
        s += t(x + 160, yy + rh / 2 + 6, "status NULL", 21 if not big else 24, WARN, MONO, "500")
        s += t(x + w - 40, yy + rh / 2 + 6, "revenue NULL", 21 if not big else 24, WARN, MONO, "500", "end")
    y2 = y + 70 + 5 * rh + (54 if not big else 70)
    s += t(x + 40, y2, "… desc nulls last, first 5 with ties", 18 if not big else 21, INK, MONO, "500")
    for i, (c, st, n, rev) in enumerate(NULLS_LAST + [TIED5]):
        yy = y2 + 18 + i * rh
        tied = i >= 4
        col = ACCENT if tied else INK
        if tied:
            s += f'<rect x="{x + 20}" y="{yy}" width="{w - 40}" height="{rh - 4}" fill="{TINT}"/>'
        s += t(x + 40, yy + rh / 2 + 6, c, 21 if not big else 24, col, MONO, "600")
        s += t(x + 160, yy + rh / 2 + 6, st, 21 if not big else 24, col, MONO, "500")
        s += t(x + w - 40, yy + rh / 2 + 6, fmt(rev), 21 if not big else 24, col, MONO, "600", "end")
    s += t(x + 40, y2 + 18 + 6 * rh + 30, "JP paid and IN paid tie for fifth", 18 if not big else 21, ACCENT, SANS, "600")
    return s


CHAIN = [("100001 <> 7920", "true", INK), ("100001 <> 15839", "true", INK),
         ("… 999,997 more", "true", SOFT), ("100001 <> NULL", "unknown", WARN)]


def art_notin(x, y, w, h, big=False):
    s = ""
    bh = 128 if not big else 146
    boxes = [("where id not in (select customer_id …)", f"{fmt(F['not_in'])} → {F['not_in_after_null']}", WARN, WARN_TINT),
             ("where not exists (… customer_id = c.id)", f"{fmt(F['not_exists'])} → {fmt(F['not_exists_after_null'])}", ACCENT, TINT)]
    for i, (q, v, col, fill) in enumerate(boxes):
        yy = y + 32 + i * (bh + 20)
        s += rect(x + 32, yy, w - 64, bh, fill, col, 8, 1.6)
        s += t(x + 60, yy + 44, q, 19 if not big else 22, INK, MONO, "500")
        s += t(x + 60, yy + bh - 28, v, 40 if not big else 46, col, MONO, "600")
        s += t(x + w - 60, yy + bh - 30, "customers with no orders", 17 if not big else 20, MUTED, SANS, "400", "end")
    cy = y + 32 + 2 * (bh + 20) + (34 if not big else 50)
    s += t(x + 40, cy, "NOT IN for customer 100,001, after the NULL:", 18 if not big else 21, MUTED, SANS, "600")
    for i, (cmp_, res, col) in enumerate(CHAIN):
        yy = cy + 40 + i * (38 if not big else 44)
        s += t(x + 60, yy, cmp_, 20 if not big else 23, col, MONO, "500")
        s += t(x + w - 60, yy, res, 20 if not big else 23, col, MONO, "600", "end")
    s += t(x + 40, cy + 40 + 4 * (38 if not big else 44) + 10, "true AND … AND unknown is unknown: the row is dropped", 18 if not big else 21, WARN, SANS, "600")
    return s


def art_fanout(x, y, w, h, big=False):
    s = ""
    bw = (w - 64 - 24) / 2
    bh = 170 if not big else 190
    pairs = [[("join orders … paid", fmt(F["join_paid"]), "one row per paid order", INK, "#fff"),
              ("exists (… paid)", fmt(F["exists_paid"]), "one row per customer", ACCENT, TINT)],
             [("union all", fmt(F["union_all"]), "333,333 + 333,333 rows", INK, "#fff"),
              ("union", fmt(F["union"]), "duplicates removed, inside each input too", ACCENT, TINT)]]
    mid = 110 if not big else 150
    top = y + (h - 2 * bh - mid) / 2
    for r, pair in enumerate(pairs):
        yy = top + r * (bh + mid)
        for c, (q, n, sub, col, fill) in enumerate(pair):
            xx = x + 32 + c * (bw + 24)
            s += rect(xx, yy, bw, bh, fill, col if col != INK else SILVER, 8, 1.6)
            s += t(xx + 24, yy + 44, q, 20 if not big else 23, INK, MONO, "500")
            s += t(xx + 24, yy + 108, n, 42 if not big else 48, col, MONO, "600")
            s += t(xx + 24, yy + bh - 24, sub, 16 if not big else 19, MUTED, SANS)
    fy = top + bh + mid / 2 + 8
    s += t(x + 40, fy, "66,667 customers × 3 paid + 33,333 × 4 = 333,333", 19 if not big else 22, MUTED, MONO, "500")
    return s


# ------------------------------------------------------------------ cards
def tr(*parts):
    return " · ".join(p for p in parts if p)


T_ORDER = tr("evaluated", "written", "rows after it",
             *[tr(f"{i + 1} {n}", w, r) for i, (n, w, r) in enumerate(ORDER)])
T_TIE = tr("order by revenue_cents desc limit 2",
           *[tr("1" if i == 0 else ("2 or 3" if c in ("IN", "JP") else str(i + 1)), c, fmt(rev))
             for i, (c, n, rev) in enumerate(REPORT)],
           "LIMIT 2", "default settings", f"DE, {SECOND['default']}", "parallel workers off",
           f"DE, {SECOND['max_parallel_workers_per_gather = 0']}", "fetch first 2 rows with ties", ", ".join(TIES))
T_JOIN = tr(*[tr(q, n, sub) for q, n, sub, _, _ in JOINS])
T_NULLSORT = tr("order by revenue_cents desc limit 5",
                *[tr(c, "status NULL", "revenue NULL") for c, _, _, _ in NULL_GROUPS],
                "… desc nulls last, first 5 with ties",
                *[tr(c, st, fmt(rev)) for c, st, _, rev in NULLS_LAST + [TIED5]],
                "JP paid and IN paid tie for fifth")
T_NOTIN = tr("where id not in (select customer_id …)", f"{fmt(F['not_in'])} → {F['not_in_after_null']}",
             "customers with no orders", "where not exists (… customer_id = c.id)",
             f"{fmt(F['not_exists'])} → {fmt(F['not_exists_after_null'])}", "customers with no orders",
             "NOT IN for customer 100,001, after the NULL:", *[tr(c, r) for c, r, _ in CHAIN],
             "true AND … AND unknown is unknown: the row is dropped")
T_FANOUT = tr("join orders … paid", fmt(F["join_paid"]), "one row per paid order",
              "exists (… paid)", fmt(F["exists_paid"]), "one row per customer",
              "union all", fmt(F["union_all"]), "333,333 + 333,333 rows",
              "union", fmt(F["union"]), "duplicates removed, inside each input too",
              "66,667 customers × 3 paid + 33,333 × 4 = 333,333")

KW = "SQL, PostgreSQL, SELECT"
FEED = [
    dict(stem="feed-01-logical-order", title="SELECT comes fifth", role="cover",
         setup="SQL evaluates a query's clauses in a fixed order, not the order you write them.",
         take="Know the order and you can predict every row count.", art=art_order,
         beat="SQL's logical order evaluates SELECT fifth, and the row count after each clause follows from it.",
         source="The problem; Worked example; Figure 2; ledger L01, L46",
         structure="Headline and setup; eight rows in evaluation order, each with its written position and the full shop's row count after it, SELECT highlighted; takeaway and footer.",
         transcript=tr("SELECT comes fifth", "SQL evaluates a query's clauses in a fixed order, not the order you write them.",
                       T_ORDER, "Know the order and you can predict every row count.", FOOT),
         alt="The eight clauses of a SELECT in evaluation order, with where each is written and the rows left after it, from 1,000,000 to 2.",
         longdesc=f"Cover card. The clauses in the order SQL evaluates them, with their written position and the row count after each, for the report 'paid revenue per country, top two' on PostgreSQL 18.6: FROM and JOIN (written 2nd) {fmt(F['inner_join'])} rows; WHERE (3rd) {fmt(F['where_paid'])}; GROUP BY (4th) 5 groups; HAVING (5th) 5; SELECT (written 1st, evaluated 5th, highlighted) 5; DISTINCT 5; ORDER BY (6th) 5 sorted; LIMIT 2 (7th) 2. Lab measurement.",
         keywords=KW + ", SQL order of execution, logical query processing"),
    dict(stem="feed-02-tie", title="Which country is second?", role="technical",
         setup="IN and JP tie on paid revenue, so LIMIT 2 has no unique answer.",
         take="A top-N query needs a tiebreaker or WITH TIES.", art=art_tie,
         beat="A tie at the LIMIT boundary let the plan choose the second row: IN with defaults, JP without parallel workers.",
         source="Worked example; Figure 3; ledger L12, L46, L47, L15",
         structure="Headline and setup; five countries ranked by paid revenue, IN and JP tinted as tied, a dashed LIMIT 2 line between them; three outcomes with the rows each returned; takeaway and footer.",
         transcript=tr("Which country is second?", "IN and JP tie on paid revenue, so LIMIT 2 has no unique answer.",
                       T_TIE, "A top-N query needs a tiebreaker or WITH TIES.", FOOT),
         alt="Five countries ranked by paid revenue with IN and JP tied on the LIMIT 2 line; defaults return DE, IN and no parallelism DE, JP.",
         longdesc=f"Paid revenue per country on PostgreSQL 18.6: DE {fmt(REPORT[0][2])} cents, then IN and JP tied at {fmt(REPORT[1][2])}, BR and US below. ORDER BY revenue DESC LIMIT 2 returned DE, {SECOND['default']} with default settings and DE, {SECOND['max_parallel_workers_per_gather = 0']} with max_parallel_workers_per_gather = 0, on the same data. FETCH FIRST 2 ROWS WITH TIES returned {', '.join(TIES)}. Rows equal on every sort key come back in an implementation-dependent order. Lab measurement.",
         keywords=KW + ", ORDER BY, LIMIT, WITH TIES, top-N query"),
    dict(stem="feed-03-left-join", title="The WHERE that undoes a LEFT JOIN", role="technical",
         setup="1,000 customers have never ordered. A WHERE on orders makes them vanish.",
         take="Put conditions for an outer join in ON.", art=art_leftjoin,
         beat="A WHERE on the right-hand table drops a left join's padded rows; the same condition in ON keeps them.",
         source="What does FROM build?; Figures 4 and 5; ledger L05, L06, L50",
         structure="Headline and setup; four stacked boxes, each a join form with its row count and what happened to the padded rows; takeaway and footer.",
         transcript=tr("The WHERE that undoes a LEFT JOIN", "1,000 customers have never ordered. A WHERE on orders makes them vanish.",
                       T_JOIN, "Put conditions for an outer join in ON.", FOOT),
         alt=f"Four join forms and their row counts: inner {fmt(F['inner_join'])}, left {fmt(F['left_join'])}, left plus WHERE {fmt(F['left_join_where_paid'])}, left with ON {fmt(F['left_join_on_paid'])}.",
         longdesc=f"customers join orders: {fmt(F['inner_join'])} rows. customers left join orders: {fmt(F['left_join'])}, one padded row for each of the {fmt(F['padded_rows'])} customers with no orders. Adding where o.status = 'paid' gives {fmt(F['left_join_where_paid'])}, the same as an inner join, because each padded row's status is NULL and NULL = 'paid' is unknown. Moving the condition into the ON clause gives {fmt(F['left_join_on_paid'])}: the padded rows survive. PostgreSQL 18.6, lab measurement.",
         keywords=KW + ", LEFT JOIN, INNER JOIN, outer join, ON vs WHERE"),
    dict(stem="feed-04-null-first", title="NULLs sort first", role="technical",
         setup="Group a left join by country and status, then sort by revenue, largest first.",
         take="Write NULLS LAST, or the empty groups win.", art=art_nullsort,
         beat="NULL sorts as larger than every value, so in a descending sort the five empty groups take the top five places.",
         source="WHERE or HAVING, and where does NULL land?; Figure 7; ledger L13, L40, L54",
         structure="Headline and setup; the five rows LIMIT 5 returns, all with NULL status and revenue; the five rows NULLS LAST returns, with the tie for fifth tinted; takeaway and footer.",
         transcript=tr("NULLs sort first", "Group a left join by country and status, then sort by revenue, largest first.",
                       T_NULLSORT, "Write NULLS LAST, or the empty groups win.", FOOT),
         alt="A descending sort's top five: five groups with NULL status and revenue; with NULLS LAST, real totals, and JP paid tied with IN paid.",
         longdesc=f"After a left join grouped by country and status, each country has one group whose status is NULL, holding its customers with no orders; its revenue is NULL. ORDER BY revenue_cents DESC LIMIT 5 returns those five groups, because PostgreSQL sorts NULL as if larger than every value. With NULLS LAST the top five are JP refunded, JP shipped, DE refunded, DE paid and JP paid, and IN paid ties JP paid at {fmt(TIED5[3])} cents. PostgreSQL 18.6, lab measurement.",
         keywords=KW + ", NULL, ORDER BY, NULLS LAST, GROUP BY"),
    dict(stem="feed-05-not-in", title="One NULL empties NOT IN", role="technical",
         setup="Customers who never ordered, before and after one order lost its customer.",
         take="Write NOT EXISTS, and declare NOT NULL.", art=art_notin,
         beat="NOT IN is a chain of ANDed inequalities, so one NULL in the subquery makes it unknown for every customer.",
         source="Why does NOT IN return nothing once a NULL appears?; Figure 8; ledger L18, L34, L58, L59, L60",
         structure="Headline and setup; two boxes with the NOT IN and NOT EXISTS counts before and after the NULL; the comparisons NOT IN makes for one customer, the last one unknown; takeaway and footer.",
         transcript=tr("One NULL empties NOT IN", "Customers who never ordered, before and after one order lost its customer.",
                       T_NOTIN, "Write NOT EXISTS, and declare NOT NULL.", FOOT),
         alt=f"NOT IN's count of customers with no orders falls from {fmt(F['not_in'])} to {F['not_in_after_null']} after one NULL; NOT EXISTS stays at {fmt(F['not_exists_after_null'])}.",
         longdesc=f"Customers who have never placed an order: NOT IN and NOT EXISTS both find {fmt(F['not_in'])}. After one order's customer_id is set to NULL, NOT IN finds {F['not_in_after_null']} and NOT EXISTS still finds {fmt(F['not_exists_after_null'])}. For customer 100,001, NOT IN compares 100001 with every customer_id: 999,999 comparisons are true and 100001 <> NULL is unknown, so the AND of all of them is unknown and WHERE drops the row. NOT EXISTS only asks whether a matching order exists. PostgreSQL 18.6, lab measurement.",
         keywords=KW + ", NOT IN, NOT EXISTS, NULL, three-valued logic"),
    dict(stem="feed-06-read-the-post", title="Where duplicates come from", role="cta",
         setup="A join repeats a row once per match; EXISTS keeps it once.",
         take="Read the full post on canery.in →", art=art_fanout,
         beat="Fan-out: a join repeats a customer once per paid order, EXISTS keeps it once, and UNION removes repeats that UNION ALL keeps.",
         source="Where do duplicate rows come from?; Figures 9 and 10; ledger L45, L55, L57",
         structure="Headline and setup; two pairs of count boxes, join against EXISTS and UNION ALL against UNION; the arithmetic behind 333,333; call to action and footer.",
         transcript=tr("Where duplicates come from", "A join repeats a row once per match; EXISTS keeps it once.",
                       T_FANOUT, "Read the full post on canery.in →", FOOT),
         alt=f"Join gives {fmt(F['join_paid'])} rows and EXISTS {fmt(F['exists_paid'])}; UNION ALL gives {fmt(F['union_all'])} rows and UNION {fmt(F['union'])}.",
         longdesc=f"Closing card. Customers with a paid order: a join returns {fmt(F['join_paid'])} rows, one per paid order, because 66,667 customers have 3 paid orders and 33,333 have 4; EXISTS returns {fmt(F['exists_paid'])}, one per customer. The customer ids of paid and of refunded orders, 333,333 rows each: UNION ALL returns {fmt(F['union_all'])}, UNION returns {fmt(F['union'])}, because it removes duplicates inside each input as well as across them. Call to action: read the full post on canery.in.",
         keywords=KW + ", JOIN, EXISTS, UNION, UNION ALL, duplicates"),
]

STORY = [
    dict(stem="story-01-logical-order", title="SELECT comes fifth", role="cover",
         setup="The order SQL evaluates a query.", take="Every row count follows from it.", art=art_order,
         overlay="The order SQL really evaluates your SELECT",
         beat="Story opener: the logical order of a SELECT, with the row count after each clause.", source=FEED[0]["source"],
         structure="Hook headline, setup line, a tall panel with the eight clauses in evaluation order, their written positions and row counts, takeaway, footer.",
         transcript=tr("SELECT comes fifth", "The order SQL evaluates a query.", T_ORDER, "Every row count follows from it.", FOOT),
         alt="Story cover: the eight clauses of a SELECT in evaluation order, SELECT fifth, with the rows left after each clause.",
         longdesc=FEED[0]["longdesc"].replace("Cover card.", "Story cover, recomposed for 9:16."),
         keywords=FEED[0]["keywords"]),
    dict(stem="story-02-tie", title="Which country is second?", role="technical",
         setup="IN and JP tie on paid revenue.", take="Add a tiebreaker or WITH TIES.", art=art_tie,
         overlay="Same query, same rows, a different second place",
         beat="Story beat: a tie at the LIMIT boundary lets the plan pick the second row.", source=FEED[1]["source"],
         structure=FEED[1]["structure"],
         transcript=tr("Which country is second?", "IN and JP tie on paid revenue.", T_TIE, "Add a tiebreaker or WITH TIES.", FOOT),
         alt="Story frame: IN and JP tied on the LIMIT 2 line; default settings keep IN, no parallel workers keep JP, WITH TIES keeps both.",
         longdesc="Story frame, recomposed for 9:16. " + FEED[1]["longdesc"],
         keywords=FEED[1]["keywords"]),
    dict(stem="story-03-not-in", title="One NULL empties NOT IN", role="technical",
         setup="1,000 customers have never ordered.", take="NOT EXISTS still finds all 1,000.", art=art_notin,
         overlay="Why NOT IN returned zero rows",
         beat="Story beat: one NULL in the subquery makes NOT IN unknown for every customer.", source=FEED[4]["source"],
         structure=FEED[4]["structure"],
         transcript=tr("One NULL empties NOT IN", "1,000 customers have never ordered.", T_NOTIN, "NOT EXISTS still finds all 1,000.", FOOT),
         alt="Story frame: NOT IN falls from 1,000 customers to 0 after one NULL, NOT EXISTS stays at 1,000, and the comparison that turns unknown.",
         longdesc="Story frame, recomposed for 9:16. " + FEED[4]["longdesc"],
         keywords=FEED[4]["keywords"]),
    dict(stem="story-04-read-the-post", title="The WHERE that undoes a LEFT JOIN", role="cta",
         setup="Conditions for an outer join belong in ON.", take="Read how → canery.in", art=art_leftjoin,
         overlay="Read how →",
         beat="Story close: the WHERE that turns a left join back into an inner join, and the call to action.", source=FEED[2]["source"],
         structure=FEED[2]["structure"],
         transcript=tr("The WHERE that undoes a LEFT JOIN", "Conditions for an outer join belong in ON.", T_JOIN, "Read how → canery.in", FOOT),
         alt="Closing story frame: inner and left join row counts, the left join undone by WHERE, and kept when the condition is in ON.",
         longdesc="Closing story frame, recomposed for 9:16, with the call to action. " + FEED[2]["longdesc"],
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
        t(72, fy, FOOT, 14 if feed else 16, ACCENT, MONO, "500", track=".14em"),
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

# Social publishing package — sql-select-evaluation-joins-group-by-null

## LinkedIn post

SQL does not evaluate your SELECT in the order you write it. SELECT is written first and evaluated fifth, after FROM, WHERE, GROUP BY and HAVING.

I built one report on PostgreSQL 18, clause by clause, and counted the rows after each: {fmt(F['inner_join'])} joined rows, {fmt(F['where_paid'])} paid orders, 5 countries, 2 shown. Then the traps:

· The "top two countries" report returned DE and {SECOND['default']} with default settings, and DE and {SECOND['max_parallel_workers_per_gather = 0']} with parallel workers off. Same query, same data. IN and JP tie, and the query never said how to break the tie.
· A LEFT JOIN kept {fmt(F['padded_rows'])} customers who had never ordered, until a WHERE on the orders table dropped them again.
· One order lost its customer, and NOT IN's count of customers who never ordered went from {fmt(F['not_in'])} to {F['not_in_after_null']}. NOT EXISTS still found all {fmt(F['not_exists_after_null'])}.

Part 5 of PostgreSQL Foundations, with a runnable lab. Swipe through the six cards; the link is in the first comment.

## LinkedIn first comment

Know the logical order and every row count becomes predictable. And wherever a NULL can appear, write NOT EXISTS, not NOT IN.

Read the full article on Canery: {CANONICAL}

## Instagram caption

SQL evaluates SELECT fifth. One PostgreSQL 18 report, built clause by clause: a tie that changes the top two between plans, a WHERE that undoes a LEFT JOIN, and one NULL that empties NOT IN. Part 5 of PostgreSQL Foundations. Full article on canery.in, link in bio.

## Shared feed order

{{feed_order}}

## Instagram Story

- CTA: Read how SQL evaluates a SELECT, clause by clause
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
