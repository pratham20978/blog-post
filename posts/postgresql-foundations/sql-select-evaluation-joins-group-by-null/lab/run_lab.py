#!/usr/bin/env python3
"""Reproducible lab for "How a SELECT Is Evaluated: Joins, Grouping and NULL" (part 5).

Every server-side number quoted in blog.md came from one run of this script. It drives a
stock PostgreSQL 18.6 with the default postgresql.conf, on a data directory on a real disk,
and writes two files next to itself:

    captures.md    the psql output of every step, verbatim, in run order
    captures.json  the numbers the figures and the article are drawn from

It builds one report clause by clause and counts the rows after every clause, twice: on the
20-row sample in sample.sql, where each count is diffed against the count worked by hand in
the article, and on the full shop (100,000 customers who ordered, 1,000 who did not, and
1,000,000 orders). Then it walks the traps the clauses set: the outer join a WHERE undoes,
WHERE against HAVING, NULL as a group and as a sort key, NOT IN against NOT EXISTS once one
NULL appears, the duplicates a join adds and EXISTS does not, UNION against UNION ALL, and
LIMIT on a tie.

Run:  PGBIN=/path/to/bin PGSOCK=/path/to/sock python3 run_lab.py
      (shopgen.py is called for you; pass --keep to reuse an existing shoplab database)
"""
import argparse
import datetime as dt
import json
import os
import pathlib
import platform
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
PGBIN = pathlib.Path(os.environ["PGBIN"])
SOCK = pathlib.Path(os.environ["PGSOCK"])
USER = os.environ.get("PGUSER", "postgres")
FULL, SAMPLE = "shoplab", "shopsample"
STAMP = "shopgen"           # the comment shopgen leaves on a database it created
NULLED_FULL, NULLED_SAMPLE = 4242, 105     # the order whose customer_id becomes NULL
NULL_MARK = "<null>"        # how psql prints NULL in the machine-read output
# NOT IN over the 1,000,000-row subquery cannot be hashed in the default 4 MB work_mem, and
# then each run takes minutes. It runs twice at the defaults, timed; every other NOT IN in
# this lab raises work_mem for its own session only. The answer does not depend on the plan.
FAST = "set work_mem = '64MB';\n"

CAP_MD = HERE / "captures.md"
CAP_JSON = HERE / "captures.json"
ENV = dict(os.environ, PGTZ="UTC")
md: list[str] = []
data: dict = {"sample": {}, "full": {}}

# The sample's answers, worked by hand from the 20 rows in sample.sql (Figure 2 of the
# article). run_lab.py diffs the server's answers against these and stops on a mismatch.
HAND = {
    "customers": 6, "orders": 14,
    "inner_join": 14, "left_join": 15,
    "where_paid": 6, "left_join_where_paid": 6, "left_join_on_paid": 7,
    "groups": 3,
    "report": [["DE", 3, 9500], ["IN", 1, 7000], ["JP", 2, 7000]],
    "first": ["DE", 3, 9500], "tied": ["IN", "JP"], "with_ties": 3,
    "having_count_ge_2": [["DE", 3, 9500], ["JP", 2, 7000]],
    "groups_country_status_inner": 9, "groups_country_status_left": 10,
    "join_paid": 6, "join_paid_distinct": 5, "in_paid": 5, "exists_paid": 5,
    "union_all": 10, "union": 5,
    "query_a_broken": [["DE", 8000, 4000], ["IN", 7000, 4000], ["JP", 7000, 11500]],
    "query_a_fixed": [["DE", 9500, 2000], ["IN", 7000, 4000], ["JP", 7000, 11500]],
    "not_in": 1, "not_exists": 1,
    "not_in_after_null": 0, "not_exists_after_null": 1,
}


def psql(sql, db=FULL, title=None, note=None, record=True, expect_error=False, tuples=False):
    """Run SQL through psql and keep its text output, exactly as a reader would see it."""
    args = [str(PGBIN / "psql"), "-X", "-q", "-h", str(SOCK), "-U", USER, "-d", db,
            "-P", "pager=off"]
    if not expect_error:
        args += ["-v", "ON_ERROR_STOP=1"]
    if tuples:
        args += ["-At", "-P", f"null={NULL_MARK}"]
    out = subprocess.run(args, input=sql, capture_output=True, text=True, env=ENV)
    if out.returncode != 0 and not expect_error:
        raise RuntimeError(f"psql failed:\n{sql}\n{out.stderr}")
    text = ((out.stdout or "") + (out.stderr or "")).rstrip("\n") if expect_error \
        else (out.stdout or "").rstrip("\n")
    if record:
        if title:
            md.append(f"**{title}** ({db})\n")
        md.append("```sql\n" + sql.strip() + "\n```\n")
        md.append("```text\n" + text + "\n```\n")
        if note:
            md.append(note + "\n")
    return text


def one(sql, db=FULL):
    return psql(sql, db=db, record=False, tuples=True)


def num(sql, db=FULL):
    return int(one(sql, db))


def rows(sql, db=FULL):
    """Rows as lists, with integers parsed and NULL as None."""
    out = []
    for line in one(sql, db).splitlines():
        cells = []
        for c in line.split("|"):
            if c == NULL_MARK:
                cells.append(None)
            else:
                try:
                    cells.append(int(c))
                except ValueError:
                    cells.append(c)
        out.append(cells)
    return out


def timed_count(sql, db=FULL, title=None, note=None, prefix=""):
    """Run one count(*) query with psql's \\timing, record it, return (count, milliseconds)."""
    text = psql("\\timing on\n" + prefix + sql + ";", db, title=title, note=note)
    lines = text.splitlines()
    sep = next(i for i, line in enumerate(lines) if set(line.strip()) == {"-"})
    # \timing prints one Time line per statement; the query is the last statement.
    ms = float(re.findall(r"Time: ([0-9.]+) ms", text)[-1])
    return int(lines[sep + 1].strip()), ms


def section(title, intro=None):
    md.append(f"\n## {title}\n")
    if intro:
        md.append(intro + "\n")
    print(f"  {title}")


def both(key, sql):
    """Run one counting query on the sample and on the full shop; diff the sample by hand."""
    s, f = num(sql, SAMPLE), num(sql, FULL)
    data["sample"][key], data["full"][key] = s, f
    if key in HAND and HAND[key] != s:
        raise SystemExit(f"hand count disagrees for {key}: by hand {HAND[key]}, server {s}")
    md.append(f"- `{key}`: sample {s:,} (by hand {HAND.get(key, '-')}), full {f:,}\n")
    return s, f


def check_hand(key, value):
    data["sample"][key] = value
    if HAND[key] != value:
        raise SystemExit(f"hand count disagrees for {key}: by hand {HAND[key]}, server {value}")


# --------------------------------------------------------------------------- the report
REPORT = """select c.country,
       count(*)            as paid_orders,
       sum(o.amount_cents) as revenue_cents
from customers c
join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country
order by revenue_cents desc
limit 2;"""

WITH_TIES = REPORT.replace("limit 2;", "fetch first 2 rows with ties;")
REPORT_ALL = REPORT.replace("\nlimit 2;", ";")

STATUS_REPORT = """select c.country, o.status,
       count(o.id)         as orders,
       sum(o.amount_cents) as revenue_cents
from customers c
left join orders o on o.customer_id = c.id
group by c.country, o.status
order by revenue_cents desc
limit 5;"""

# The six queries of exercise E3: which of them change when one order loses its customer?
SIX = {
    "q1_join_count": "select count(*) from customers c join orders o on o.customer_id = c.id",
    "q2_in": "select count(*) from customers where id in (select customer_id from orders)",
    "q3_not_in": "select count(*) from customers where id not in (select customer_id from orders)",
    "q4_not_exists": "select count(*) from customers c "
                     "where not exists (select 1 from orders o where o.customer_id = c.id)",
    "q5_count_distinct": "select count(distinct customer_id) from orders",
    "q6_groups": "select count(*) from (select customer_id from orders group by customer_id) g",
}

QUERY_A_FIXED = """select c.country,
       sum(o.amount_cents) filter (where o.status = 'paid')     as paid_cents,
       sum(o.amount_cents) filter (where o.status = 'refunded') as refunded_cents
from customers c
join orders o on o.customer_id = c.id
group by c.country
order by c.country"""
QUERY_B_FIXED = """select count(*) as customers_without_orders
from customers c
where not exists (select 1 from orders o where o.customer_id = c.id)"""
QUERY_C_FIXED = """select c.country, count(*) as big_orders
from customers c
join orders o on o.customer_id = c.id
where o.amount_cents >= 90000
group by c.country
order by c.country"""


def broken_queries():
    """The three queries in broken.sql, split on their marker lines."""
    text = (HERE / "broken.sql").read_text()
    parts, current, key = {}, [], None
    for line in text.splitlines():
        if line.startswith("-- A.") or line.startswith("-- B.") or line.startswith("-- C."):
            if key:
                parts[key] = "\n".join(current).strip()
            key, current = line[3], []
        elif key and not line.startswith("--"):
            current.append(line)
    parts[key] = "\n".join(current).strip()
    return {k: v.rstrip(";") for k, v in parts.items()}


def load_sample():
    exists = one(f"select 1 from pg_database where datname = '{SAMPLE}'", "postgres") == "1"
    if exists:
        mine = one(f"select shobj_description(oid, 'pg_database') from pg_database "
                   f"where datname = '{SAMPLE}'", "postgres")
        if mine != STAMP:
            raise SystemExit(f"database {SAMPLE} exists and was not created by this lab")
        psql(f'drop database "{SAMPLE}"', "postgres", record=False)
    psql(f'create database "{SAMPLE}"', "postgres", record=False)
    psql(f"comment on database \"{SAMPLE}\" is '{STAMP}'", "postgres", record=False)
    psql((HERE / "sample.sql").read_text(), SAMPLE, record=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true", help="reuse an existing shoplab database")
    a = ap.parse_args()

    if not a.keep:
        print("shopgen...")
        subprocess.run([sys.executable, str(HERE / "shopgen.py"), "--scale", "M",
                        "--orderless", "1000", "--db", FULL, "--drop",
                        "--bin", str(PGBIN), "--sock", str(SOCK), "--user", USER], check=True)
    load_sample()

    started = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    version = one("select version()")
    data["provenance"] = {
        "captured_utc": started.isoformat(),
        "server_version": version,
        "os": f"{platform.system()} {platform.release()}",
        "cpus": os.cpu_count(),
        "python": platform.python_version(),
        "settings": {k: v for k, v in (r.split("|") for r in one(
            "select name || '|' || setting from pg_settings where name in "
            "('shared_buffers','work_mem','max_parallel_workers_per_gather',"
            "'enable_hashagg','block_size','lc_collate') order by name").splitlines())},
    }
    md.append("# Captures - how a SELECT is evaluated\n")
    md.append(f"Captured {started.isoformat()} on {platform.system()} "
              f"{platform.release()}, {os.cpu_count()} CPUs.\n")
    md.append(f"`{version}`, default `postgresql.conf`.\n")

    # ------------------------------------------------------------- 1. the data
    section("1. The data: the full shop and the 20-row sample",
            "shopgen built the series' two tables at scale M and added 1,000 customers who "
            "have never ordered. sample.sql built the 20-row sample by hand.")
    psql("""select count(*) as customers,
       count(*) filter (where id > 100000) as added_without_orders
from customers;""", title="Customers in the full shop")
    psql("""select orders_placed, count(*) as customers
from (select c.id, count(o.id) as orders_placed
      from customers c left join orders o on o.customer_id = c.id
      group by c.id) per_customer
group by orders_placed
order by orders_placed;""", title="How many orders each customer has placed",
         note="Every one of the original 100,000 customers has exactly 10 orders: the "
              "generator's multiplier 7,919 shares no factor with 100,000, so customer_id "
              "visits every customer once in every 100,000 orders.")
    data["full"]["orders_per_customer"] = rows("""select orders_placed, count(*)
from (select c.id, count(o.id) as orders_placed
      from customers c left join orders o on o.customer_id = c.id group by c.id) x
group by orders_placed order by orders_placed""")
    data["full"]["paid_per_customer"] = rows("""select paid, count(*)
from (select customer_id, count(*) as paid from orders where status = 'paid'
      group by customer_id) x group by paid order by paid""")
    psql("table customers;", SAMPLE, title="The sample's customers")
    psql("table orders order by id;", SAMPLE, title="The sample's orders")

    # ------------------------------------------------------------- 2. the report
    section("2. One report, clause by clause",
            "Paid revenue per country, top two. Each step adds one clause, and the row "
            "count is taken after it, on the sample and on the full shop.")
    psql(REPORT, title="The report")
    psql(REPORT, SAMPLE, title="The report on the sample")
    md.append("Row counts after each clause:\n")
    both("customers", "select count(*) from customers c")
    both("inner_join", "select count(*) from customers c join orders o on o.customer_id = c.id")
    both("where_paid", "select count(*) from customers c join orders o on o.customer_id = c.id "
                       "where o.status = 'paid'")
    both("groups", "select count(*) from (select c.country from customers c join orders o "
                   "on o.customer_id = c.id where o.status = 'paid' group by c.country) g")
    rep_s = rows(REPORT_ALL.rstrip(";"), SAMPLE)
    rep_f = rows(REPORT_ALL.rstrip(";"), FULL)
    check_hand("report", sorted(rep_s))
    data["full"]["report_ordered"] = rep_f
    psql(REPORT_ALL, title="ORDER BY without LIMIT: IN and JP have the same revenue")
    check_hand("first", rep_s[0])
    check_hand("tied", sorted(r[0] for r in rep_s[1:]))
    lim_s, lim_f = rows(REPORT.rstrip(";"), SAMPLE), rows(REPORT.rstrip(";"), FULL)
    data["sample"]["limit_2"], data["full"]["limit_2"] = lim_s, lim_f
    wt_s, wt_f = rows(WITH_TIES.rstrip(";"), SAMPLE), rows(WITH_TIES.rstrip(";"), FULL)
    check_hand("with_ties", len(wt_s))
    data["full"]["with_ties"] = wt_f
    psql(WITH_TIES, title="FETCH FIRST 2 ROWS WITH TIES keeps both tied rows")
    psql(f"explain (costs off) {REPORT}", title="The plan: a top-N sort under the limit")

    # Which country comes second is not promised. Ask the same question under different
    # plans; one psql call is one session, so each SET travels with its query.
    variants = {
        "default": "",
        "enable_hashagg = off": "set enable_hashagg = off;\n",
        "max_parallel_workers_per_gather = 0": "set max_parallel_workers_per_gather = 0;\n",
        "both": "set enable_hashagg = off;\nset max_parallel_workers_per_gather = 0;\n",
        "enable_sort = off": "set enable_sort = off;\n",
    }
    second = {}
    for name, prefix in variants.items():
        out = psql(prefix + REPORT, record=False, tuples=True).splitlines()
        second[name] = out[1].split("|")[0] if len(out) > 1 else None
    data["full"]["second_row_by_plan"] = second
    md.append("Second row of `LIMIT 2` under different planner settings: "
              + ", ".join(f"{k}: **{v}**" for k, v in second.items()) + "\n")
    serial = "set max_parallel_workers_per_gather = 0;\n"
    psql(serial + f"explain (costs off) {REPORT}",
         title="With parallel workers off: a hash aggregate, and no sort by country before it")
    groups_q = REPORT_ALL.split("\norder by")[0]
    psql(groups_q + ";", title="The order the default plan hands the five groups on")
    psql(serial + groups_q + ";", title="The order the hash aggregate hands them on")
    data["full"]["group_order_default"] = [r[0] for r in rows(groups_q)]
    data["full"]["group_order_no_parallel"] = [r[0] for r in rows(serial + groups_q)]
    s_second = {}
    for name, prefix in variants.items():
        out = psql(prefix + REPORT, SAMPLE, record=False, tuples=True).splitlines()
        s_second[name] = out[1].split("|")[0] if len(out) > 1 else None
    data["sample"]["second_row_by_plan"] = s_second
    md.append("Same, on the sample: " + ", ".join(f"{k}: **{v}**" for k, v in s_second.items())
              + "\n")

    # ------------------------------------------------------------- 3. joins
    section("3. FROM: inner join, left join, and the WHERE that undoes one")
    both("left_join", "select count(*) from customers c left join orders o on o.customer_id = c.id")
    both("left_join_where_paid", "select count(*) from customers c left join orders o "
                                 "on o.customer_id = c.id where o.status = 'paid'")
    both("left_join_on_paid", "select count(*) from customers c left join orders o "
                              "on o.customer_id = c.id and o.status = 'paid'")
    psql("""select c.id, c.country, o.id as order_id, o.amount_cents, o.status
from customers c
left join orders o on o.customer_id = c.id
where c.id = 6;""", SAMPLE, title="Customer 6 after the LEFT JOIN: one row, padded with NULLs")
    psql("""select count(*) filter (where o.id is null) as padded_rows,
       count(*) as all_rows
from customers c left join orders o on o.customer_id = c.id;""",
         title="The full shop: 1,000 padded rows")
    psql("""select c.country, count(o.id) as paid_orders
from customers c
left join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country order by c.country;""", SAMPLE,
         title="LEFT JOIN, then WHERE on the right table: customer 6 is gone again")
    psql("""select c.country, count(o.id) as paid_orders
from customers c
left join orders o on o.customer_id = c.id and o.status = 'paid'
group by c.country order by c.country;""", SAMPLE,
         title="The same condition in ON: customer 6 stays, with 0 paid orders")
    data["full"]["padded_rows"] = num("select count(*) from customers c left join orders o "
                                      "on o.customer_id = c.id where o.id is null")
    psql("explain (costs off) select count(*) from customers c left join orders o "
         "on o.customer_id = c.id where o.status = 'paid';",
         title="The planner agrees: a LEFT JOIN with that WHERE is an inner join",
         note="No Left Join node: the WHERE clause rejects every padded row, so the planner "
              "reduced the outer join to an inner one.")

    # ------------------------------------------------------------- 4. WHERE and HAVING
    section("4. WHERE filters rows, HAVING filters groups")
    where_q = """select c.country, o.status, count(*) as orders
from customers c join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country, o.status
order by c.country"""
    having_q = """select c.country, o.status, count(*) as orders
from customers c join orders o on o.customer_id = c.id
group by c.country, o.status
having o.status = 'paid'
order by c.country"""
    psql(where_q + ";", title="status = 'paid' in WHERE")
    psql(having_q + ";", title="The same predicate in HAVING")
    data["full"]["where_vs_having_same_rows"] = rows(where_q) == rows(having_q)
    data["full"]["rows_into_grouping_where"] = data["full"]["where_paid"]
    data["full"]["rows_into_grouping_having"] = data["full"]["inner_join"]
    data["full"]["groups_formed_where"] = num(f"select count(*) from ({where_q}) g")
    data["full"]["groups_formed_having"] = num(
        "select count(*) from (select c.country, o.status from customers c join orders o "
        "on o.customer_id = c.id group by c.country, o.status) g")
    pw = psql(f"explain (costs off) {where_q};", title="Plan with WHERE")
    ph = psql(f"explain (costs off) {having_q};", title="Plan with HAVING",
              note="Identical. The planner moved a HAVING condition that uses no aggregate "
                   "into WHERE, so the rows are filtered before they are grouped.")
    data["full"]["where_having_plans_identical"] = pw == ph
    data["full"]["plan_having"] = ph
    psql("""select c.country, count(*) as orders
from customers c join orders o on o.customer_id = c.id
where count(*) > 66666
group by c.country;""", title="A condition on an aggregate cannot go in WHERE",
         expect_error=True)
    psql("""select c.country, o.status, count(*) as orders
from customers c join orders o on o.customer_id = c.id
group by c.country, o.status
having count(*) > 66666
order by c.country, o.status;""", title="It goes in HAVING: 10 of the 15 groups pass")
    data["full"]["having_count_gt_66666"] = num(
        "select count(*) from (select 1 from customers c join orders o on o.customer_id = c.id "
        "group by c.country, o.status having count(*) > 66666) g")
    hv = rows("""select c.country, count(*), sum(o.amount_cents) from customers c
join orders o on o.customer_id = c.id where o.status = 'paid'
group by c.country having count(*) >= 2 order by c.country""", SAMPLE)
    check_hand("having_count_ge_2", hv)
    psql("""select c.country, sum(o.amount_cents) as revenue_cents
from customers c join orders o on o.customer_id = c.id
where revenue_cents > 3333300000
group by c.country;""", title="A SELECT alias does not exist yet in WHERE", expect_error=True)
    psql("""select c.country, sum(o.amount_cents) as revenue_cents
from customers c join orders o on o.customer_id = c.id
group by c.country
order by revenue_cents desc;""", title="It does exist in ORDER BY")
    psql("""select c.country, sum(o.amount_cents) as revenue_cents
from customers c join orders o on o.customer_id = c.id
group by c.country
order by revenue_cents / 100 desc;""",
         title="But only on its own, not inside an expression", expect_error=True)

    # ------------------------------------------------------------- 5. NULL as a group
    section("5. GROUP BY puts the NULLs in one group, and DESC sorts them first")
    both("groups_country_status_inner", "select count(*) from (select 1 from customers c "
         "join orders o on o.customer_id = c.id group by c.country, o.status) g")
    both("groups_country_status_left", "select count(*) from (select 1 from customers c "
         "left join orders o on o.customer_id = c.id group by c.country, o.status) g")
    psql("""select c.country, o.status, count(*) as rows_in_group,
       count(o.id) as orders, sum(o.amount_cents) as revenue_cents
from customers c
left join orders o on o.customer_id = c.id
group by c.country, o.status
having o.status is null
order by c.country;""", title="The five groups whose status is NULL",
         note="Each holds 200 padded rows: count(*) counts them, count(o.id) does not, and "
              "sum over no values is NULL.")
    data["full"]["null_groups"] = rows("""select c.country, count(*), count(o.id),
sum(o.amount_cents) from customers c left join orders o on o.customer_id = c.id
group by c.country, o.status having o.status is null order by c.country""")
    psql(STATUS_REPORT, title="Top five by revenue: the NULL groups come first",
         note="NULLS FIRST is the default for DESC: a NULL sorts as if larger than every value.")
    data["full"]["status_report_top5"] = rows(STATUS_REPORT.rstrip(";"))
    nl = STATUS_REPORT.replace("revenue_cents desc", "revenue_cents desc nulls last")
    psql(nl, title="With NULLS LAST")
    data["full"]["status_report_nulls_last"] = rows(nl.rstrip(";"))
    nl_all = nl.replace("\nlimit 5;", "")
    data["full"]["status_report_nulls_last_all"] = rows(nl_all)
    wt5 = nl.replace("limit 5;", "fetch first 5 rows with ties;")
    psql(wt5, title="NULLS LAST, five rows with ties")
    data["full"]["status_report_with_ties"] = rows(wt5.rstrip(";"))
    psql("""select c.country, o.status, count(o.id) as orders, sum(o.amount_cents) as revenue_cents
from customers c left join orders o on o.customer_id = c.id
group by c.country, o.status order by revenue_cents desc;""", SAMPLE,
         title="The sample: one NULL group, first")

    # ------------------------------------------------------------- 6. EXISTS, IN, JOIN
    section("6. EXISTS and IN keep each customer once; a JOIN repeats it")
    both("join_paid", "select count(*) from customers c join orders o on o.customer_id = c.id "
                      "where o.status = 'paid'")
    both("join_paid_distinct", "select count(*) from (select distinct c.id from customers c "
                               "join orders o on o.customer_id = c.id where o.status = 'paid') d")
    both("in_paid", "select count(*) from customers c "
                    "where c.id in (select customer_id from orders where status = 'paid')")
    both("exists_paid", "select count(*) from customers c where exists "
                        "(select 1 from orders o where o.customer_id = c.id and o.status = 'paid')")
    psql("""explain (costs off) select c.id from customers c
where exists (select 1 from orders o where o.customer_id = c.id and o.status = 'paid');""",
         title="EXISTS: the planner removes duplicate customer ids before it joins",
         note="The HashAggregate grouped by o.customer_id keeps each customer id once, so the "
              "join above it can match each customer at most once: a semi-join.")
    psql("""explain (costs off) select c.id from customers c
where c.id in (select customer_id from orders where status = 'paid');""",
         title="IN gets the same plan")
    psql("""select c.id, count(*) as rows_after_join
from customers c join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.id order by c.id;""", SAMPLE, title="Customer 1 appears twice after the join")

    bq = broken_queries()
    a_s = rows(bq["A"], SAMPLE)
    check_hand("query_a_broken", a_s)
    check_hand("query_a_fixed", rows(QUERY_A_FIXED, SAMPLE))
    psql(bq["A"] + ";", title="Two joins to orders multiply each other")
    psql(QUERY_A_FIXED + ";", title="One join, two filtered sums")
    data["full"]["query_a_broken"] = rows(bq["A"])
    data["full"]["query_a_fixed"] = rows(QUERY_A_FIXED)
    data["full"]["query_a_rows_before_grouping"] = num(
        "select count(*) from customers c join orders p on p.customer_id = c.id and "
        "p.status = 'paid' join orders r on r.customer_id = c.id and r.status = 'refunded'")
    psql(bq["A"] + ";", SAMPLE, title="Query A on the sample")
    psql(QUERY_A_FIXED + ";", SAMPLE, title="Its repair on the sample")

    # ------------------------------------------------------------- 7. UNION
    section("7. UNION removes duplicates, inside each input as well as across them")
    paid_ids = "select customer_id from orders where status = 'paid'"
    ref_ids = "select customer_id from orders where status = 'refunded'"
    both("union_all", f"select count(*) from ({paid_ids} union all {ref_ids}) u")
    both("union", f"select count(*) from ({paid_ids} union {ref_ids}) u")
    data["full"]["paid_ids_rows"] = num(f"select count(*) from ({paid_ids}) p")
    data["full"]["refunded_ids_rows"] = num(f"select count(*) from ({ref_ids}) r")
    psql(f"""select count(*) from ({paid_ids}
union all
{ref_ids}) u;""", title="UNION ALL keeps every row")
    psql(f"""select count(*) from ({paid_ids}
union
{ref_ids}) u;""", title="UNION keeps each distinct value once")
    psql(f"select count(*) from ({paid_ids} union {paid_ids}) u;",
         title="Even a query UNIONed with itself is deduplicated")
    data["full"]["paid_union_itself"] = num(f"select count(*) from ({paid_ids} union {paid_ids}) u")

    # ------------------------------------------------------------- 8. NOT IN vs NOT EXISTS
    section("8. NOT IN and NOT EXISTS agree, until one NULL appears")
    anti = {
        "not_in": "select count(*) from customers where id not in (select customer_id from orders)",
        "not_exists": "select count(*) from customers c where not exists "
                      "(select 1 from orders o where o.customer_id = c.id)",
        "left_join_is_null": "select count(*) from customers c left join orders o "
                             "on o.customer_id = c.id where o.id is null",
        "except": "select count(*) from (select id from customers "
                  "except select customer_id from orders) e",
    }
    check_hand("not_in", num(anti["not_in"], SAMPLE))
    check_hand("not_exists", num(anti["not_exists"], SAMPLE))
    f, ms = timed_count(anti["not_in"], title="Customers with no orders, by NOT IN "
                                              "(default settings, timed)")
    data["full"]["not_in"], data["full"]["not_in_ms"] = f, ms
    f, ms = timed_count(anti["not_exists"], title="By NOT EXISTS (timed)")
    data["full"]["not_exists"], data["full"]["not_exists_ms"] = f, ms
    for k in ("left_join_is_null", "except"):
        data["full"][k] = num(anti[k])
    data["full"]["six_before"] = {k: (data["full"]["not_in"] if k == "q3_not_in" else num(q))
                                  for k, q in SIX.items()}
    psql("explain (costs off) " + anti["not_in"] + ";",
         title="NOT IN stays a filter, and its subquery is re-read, not hashed",
         note="Not hashed: 1,000,000 rows of about 32 bytes each do not fit in 4 MB x "
              "hash_mem_multiplier 2, so the Materialize node is scanned for each customer.")
    psql("explain (costs off) " + anti["not_exists"] + ";", title="NOT EXISTS becomes an anti-join")
    f, ms = timed_count(anti["not_in"], prefix=FAST,
                        title="NOT IN again, with work_mem = 64MB for this session (timed)")
    data["full"]["not_in_hashed_ms"] = ms
    if f != data["full"]["not_in"]:
        raise SystemExit("NOT IN gave a different answer with a different plan")
    psql(FAST + "explain (costs off) " + anti["not_in"] + ";",
         title="With 64 MB the subquery is hashed")
    auto_before = one("select count(*) from pg_file_settings where sourcefile like '%auto.conf'",
                      "postgres")
    data["postgresql_auto_conf_entries_before"] = int(auto_before)

    psql("alter table orders alter column customer_id drop not null;",
         title="Let customer_id be NULL", note="shopgen declared it NOT NULL; this is the one "
                                              "change that lets the next statement work.")
    psql(f"update orders set customer_id = null where id = {NULLED_FULL};",
         title=f"Order {NULLED_FULL} loses its customer")
    psql("alter table orders alter column customer_id drop not null;", SAMPLE, record=False)
    psql(f"update orders set customer_id = null where id = {NULLED_SAMPLE};", SAMPLE,
         title=f"In the sample, order {NULLED_SAMPLE} loses its customer")
    check_hand("not_in_after_null", num(anti["not_in"], SAMPLE))
    check_hand("not_exists_after_null", num(anti["not_exists"], SAMPLE))
    f, ms = timed_count(anti["not_in"], title="NOT IN now finds no one (default settings, timed)")
    data["full"]["not_in_after_null"], data["full"]["not_in_after_null_ms"] = f, ms
    f, ms = timed_count(anti["not_exists"], title="NOT EXISTS still finds the same 1,000 (timed)")
    data["full"]["not_exists_after_null"], data["full"]["not_exists_after_null_ms"] = f, ms
    for k in ("left_join_is_null", "except"):
        data["full"][k + "_after_null"] = num(anti[k])
    data["full"]["six_after"] = {k: (data["full"]["not_in_after_null"] if k == "q3_not_in"
                                     else num(q)) for k, q in SIX.items()}
    data["full"]["six_changed"] = [k for k in SIX
                                   if data["full"]["six_before"][k] != data["full"]["six_after"][k]]
    filtered = ("select count(*) from customers where id not in (select customer_id from orders\n"
                "                                         where customer_id is not null)")
    psql(FAST + filtered + ";", title="NOT IN works again once the NULL is filtered out "
                                      "of the subquery (work_mem = 64MB for speed)")
    data["full"]["not_in_filtered_after_null"] = num(FAST + filtered)
    psql("""select 100001 not in (1, 2, null) as one_null,
       100001 not in (1, 2)       as no_null,
       100001 <> null              as compare_with_null;""",
         title="Why: NOT IN is a chain of <> comparisons joined by AND")
    psql(f"""select count(*) as groups from (select customer_id from orders
                              group by customer_id) g;""",
         title="GROUP BY gives the NULL a group of its own")
    psql(f"""select count(*) from ({paid_ids} union {ref_ids}) u;""",
         title="UNION keeps one NULL")
    data["full"]["union_after_null"] = num(f"select count(*) from ({paid_ids} union {ref_ids}) u")
    data["full"]["union_all_after_null"] = num(
        f"select count(*) from ({paid_ids} union all {ref_ids}) u")
    md.append("The six queries of exercise E3, before and after the NULL:\n")
    for k in SIX:
        md.append(f"- `{k}`: {data['full']['six_before'][k]:,} → {data['full']['six_after'][k]:,}\n")

    # Exercise E4's reference answers, in the state check.py e4 --break sets up.
    data["full"]["e4_reference"] = {"A": rows(QUERY_A_FIXED), "B": rows(QUERY_B_FIXED),
                                    "C": rows(QUERY_C_FIXED)}
    # Query B is the NOT IN above, already run at the defaults; it is not run a third time.
    data["full"]["e4_broken"] = {"A": rows(bq["A"]), "B": [[data["full"]["not_in_after_null"]]],
                                 "C": rows(bq["C"])}
    psql(QUERY_B_FIXED + ";", title="Query B's repair")
    psql("""select c.country, count(*) as big_orders
from customers c join orders o on o.customer_id = c.id
group by c.country
having o.amount_cents >= 90000;""", title="Query C's first draft, and the error that started it",
         expect_error=True)
    psql(bq["C"] + ";", title="Query C as shipped")
    psql(QUERY_C_FIXED + ";", title="Its repair")

    # ------------------------------------------------------------- 9. three differences
    section("9. Three ways to write R minus S, three answers",
            "The example from Guagliardo and Libkin (PVLDB 2017): R = {1, NULL}, S = {NULL}.")
    rs = "with r(a) as (values (1), (null::int)), s(a) as (values (null::int))\n"
    diff = {
        "not_in": rs + "select a from r where a not in (select a from s)",
        "not_exists": rs + "select a from r where not exists (select 1 from s where s.a = r.a)",
        "except": rs + "select a from r except select a from s",
    }
    data["three_differences"] = {}
    for k, q in diff.items():
        psql(q + " order by a;", "postgres", title=f"R minus S by {k.replace('_', ' ').upper()}")
        data["three_differences"][k] = [r[0] for r in rows(q + " order by a", "postgres")]

    auto_after = one("select count(*) from pg_file_settings where sourcefile like '%auto.conf'",
                     "postgres")
    data["postgresql_auto_conf_entries_after"] = int(auto_after)

    # ------------------------------------------------------------- write
    CAP_MD.write_text("\n".join(md) + "\n")
    CAP_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {CAP_MD.name} ({CAP_MD.stat().st_size:,} B) and "
          f"{CAP_JSON.name} ({CAP_JSON.stat().st_size:,} B)")


if __name__ == "__main__":
    main()
