#!/usr/bin/env python3
"""Reproducible lab for "What a Relational Database Actually Does" (part 4).

Every server-side number quoted in blog.md came from one run of this script. It drives a
stock PostgreSQL 18.6 built from source, with the default postgresql.conf, on a data
directory on a real disk, and writes two files next to itself:

    captures.md    the psql output of every step, verbatim, in run order
    captures.json  the numbers the figures and the article are drawn from

It asks one business question of the series' two tables - revenue per country for paid
orders - and follows it through the four stages the server puts it through: parse,
rewrite, plan, execute. Then it breaks the answer twice, with the two facts about SQL
that surprise people who learned the relational model first: `orders` has no primary key,
so a duplicate row is legal; and NULL is not a value, so count(*) and count(amount_cents)
stop agreeing.

Run:  PGBIN=/path/to/bin PGSOCK=/path/to/sock python3 run_lab.py
      (shopgen.py is called for you; pass --keep to reuse an existing shoplab database)
"""
import argparse
import datetime as dt
import json
import os
import pathlib
import platform
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
PGBIN = pathlib.Path(os.environ["PGBIN"])
SOCK = pathlib.Path(os.environ["PGSOCK"])
USER = os.environ.get("PGUSER", "postgres")
DB = "shoplab"
ROW_ID = 4242

CAP_MD = HERE / "captures.md"
CAP_JSON = HERE / "captures.json"
ENV = dict(os.environ, PGTZ="UTC")
md: list[str] = []
data: dict = {}


def psql(sql, db=DB, title=None, note=None, record=True, expect_error=False, tuples=False):
    """Run SQL through psql and keep its text output, exactly as a reader would see it."""
    args = [str(PGBIN / "psql"), "-X", "-q", "-h", str(SOCK), "-U", USER, "-d", db,
            "-P", "pager=off"]
    if not expect_error:
        args += ["-v", "ON_ERROR_STOP=1"]
    if tuples:
        args += ["-At"]
    out = subprocess.run(args, input=sql, capture_output=True, text=True, env=ENV)
    if out.returncode != 0 and not expect_error:
        raise RuntimeError(f"psql failed:\n{sql}\n{out.stderr}")
    text = ((out.stdout or "") + (out.stderr or "")).rstrip("\n") if expect_error \
        else (out.stdout or "").rstrip("\n")
    if record:
        if title:
            md.append(f"**{title}**\n")
        md.append("```sql\n" + sql.strip() + "\n```\n")
        md.append("```text\n" + text + "\n```\n")
        if note:
            md.append(note + "\n")
    return text


def one(sql, db=DB):
    return psql(sql, db=db, record=False, tuples=True)


def section(title, intro=None):
    md.append(f"\n## {title}\n")
    if intro:
        md.append(intro + "\n")
    print(f"  {title}")


# --------------------------------------------------------------------------- the question
QUESTION = """select c.country,
       sum(o.amount_cents) as revenue_cents,
       count(*)            as paid_orders
from customers c
join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country
order by revenue_cents desc;"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true", help="reuse an existing shoplab database")
    a = ap.parse_args()

    if not a.keep:
        print("shopgen...")
        subprocess.run([sys.executable, str(HERE / "shopgen.py"), "--scale", "M", "--db", DB,
                        "--drop", "--bin", str(PGBIN), "--sock", str(SOCK), "--user", USER],
                       check=True)

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
            "('shared_buffers','work_mem','seq_page_cost','random_page_cost',"
            "'effective_cache_size','max_parallel_workers_per_gather','block_size') "
            "order by name").splitlines())},
    }
    md.append(f"# Captures - what a relational database actually does\n")
    md.append(f"Captured {started.isoformat()} on {platform.system()} "
              f"{platform.release()}, {os.cpu_count()} CPUs.\n")
    md.append(f"`{version}`, default `postgresql.conf`.\n")

    # ---------------------------------------------------------------- 1. the two relations
    section("1. Two tables, and the same two tables as rows in the catalog",
            "The schema is data. Every table in this database has a row in `pg_class`, and "
            "every column has a row in `pg_attribute` - including the tables that store "
            "`pg_class` and `pg_attribute` themselves.")

    psql("\\d customers", title="The customers table as psql describes it")
    psql("\\d orders", title="The orders table - note what it does not have")

    psql("""select relname, relkind, relnatts, relpages, reltuples::bigint as reltuples,
       relhasindex, pg_size_pretty(pg_relation_size(oid)) as size
from pg_class
where relname in ('customers','orders')
order by relname;""",
         title="The two tables, as rows in pg_class",
         note="`relpages` and `reltuples` are the planner's estimates, refreshed by "
              "VACUUM and ANALYZE - shopgen ran both.")

    psql("""select attname, atttypid::regtype as type, attnum, attlen, attnotnull
from pg_attribute
where attrelid = 'orders'::regclass and attnum > 0
order by attnum;""",
         title="The columns of orders, as rows in pg_attribute",
         note="Ordinary columns are numbered from 1 up; the system columns, such as `ctid`, "
              "have negative attnum and are filtered out here.")

    psql("""select relname, relkind, relnatts
from pg_class
where relname in ('pg_class','pg_attribute')
order by relname;""",
         title="pg_class has a row for pg_class",
         note="The catalog describes itself. That is Codd's point made concrete: there is "
              "one kind of thing in the database, and it is the relation.")

    for t in ("customers", "orders"):
        data[f"{t}_relpages"] = int(one(
            f"select relpages from pg_class where relname = '{t}'"))
        data[f"{t}_reltuples"] = int(float(one(
            f"select reltuples from pg_class where relname = '{t}'")))
    data["orders_natts"] = int(one("select relnatts from pg_class where relname='orders'"))
    data["pg_class_natts"] = int(one("select relnatts from pg_class where relname='pg_class'"))

    # ---------------------------------------------------------------- 2. the question
    section("2. One business question, asked once",
            "Revenue in cents per country, for paid orders only.")
    psql(QUESTION, title="The question, and its answer")
    rows = one(QUESTION.replace(";", "") + "")
    data["revenue_clean"] = [r.split("|") for r in rows.splitlines()]
    data["revenue_total_clean"] = int(one(
        "select sum(o.amount_cents) from customers c join orders o on o.customer_id = c.id "
        "where o.status = 'paid'"))
    data["paid_orders_clean"] = int(one(
        "select count(*) from orders where status = 'paid'"))

    # ---------------------------------------------------------------- 3. the four stages
    section("3. What the server did with it: parse, rewrite, plan, execute",
            "The four stages are PostgreSQL's own (docs ch. 51, 'The Path of a Query'). "
            "Each one can be made to show itself.")

    psql("selec c.country from customers c;", title="Stage 1a, the parser: a syntax error",
         expect_error=True,
         note="The parser only checks the shape of the text. It has not looked anything up "
              "yet, which is why it reports a position and not a name.")

    psql("select c.nosuchcolumn from customers c;",
         title="Stage 1b, the transformation: a name that does not exist",
         expect_error=True,
         note="This is the second half of the parser stage. Now the server has consulted the "
              "catalog, found `customers`, and failed to find a column in it.")

    psql("""create view paid_revenue as
select c.country, sum(o.amount_cents) as revenue_cents, count(*) as paid_orders
from customers c join orders o on o.customer_id = c.id
where o.status = 'paid'
group by c.country;""", title="Stage 2, the rewriter: define a view")

    psql("explain (costs off) select * from paid_revenue order by revenue_cents desc;",
         title="Stage 2, the rewriter: the view is gone by planning time",
         note="There is no 'view scan' node. The rewriter replaced `paid_revenue` with its "
              "definition before the planner ever saw the query.")

    psql("explain select * from paid_revenue order by revenue_cents desc;",
         title="Stage 3, the planner: the same plan, with costs", record=True)
    psql(f"explain {QUESTION}", title="Stage 3, the planner: the plan it chose for our query",
         note="Two numbers per node: the cost before the first row, and the cost of running "
              "the node to completion. The units are arbitrary, anchored at "
              "`seq_page_cost = 1`.")

    plan_default = psql(f"explain (analyze, timing off, summary off) {QUESTION}",
                        title="Stage 4, the executor: the same plan, actually run",
                        note="`actual rows` beside `rows` is the planner's estimate graded "
                             "against reality. PostgreSQL 18 prints those actual row counts "
                             "with two decimal places, and includes BUFFERS by default; on "
                             "16 and 17 you ask for buffers explicitly.")
    data["explain_analyze_default"] = plan_default

    # One psql call is one session. A SET sent in its own call is gone before the next
    # call starts, so the SET must travel in the same call as the EXPLAIN it changes.
    psql(f"set enable_hashjoin = off;\nexplain {QUESTION}",
         title="Stage 3 again: take the cheapest plan away, and see the planner's second choice",
         note="Turning off the hash join does not forbid an answer, it forbids one path to "
              "it. The cost the planner reports here is what it avoided by choosing the "
              "first plan. How those costs are computed is covered later in the series.")

    # Each psql call is its own session, so the SET and the EXPLAIN must travel together.
    j = json.loads(one(f"explain (format json) {QUESTION}"))
    data["cost_plan_chosen"] = {"total_cost": j[0]["Plan"]["Total Cost"],
                                "top_node": j[0]["Plan"]["Node Type"]}
    j = json.loads(one(f"set enable_hashjoin = off; explain (format json) {QUESTION}"))
    data["cost_plan_runner_up"] = {"total_cost": j[0]["Plan"]["Total Cost"],
                                   "top_node": j[0]["Plan"]["Node Type"]}

    # ---------------------------------------------------------------- 4. surprise one
    section("4. The first surprise: orders has no primary key",
            "A relation, in Codd's sense, is a set: no two rows are the same. A SQL table "
            "is not a set unless you say so.")

    psql(f"select id, customer_id, amount_cents, status from orders where id = {ROW_ID};",
         title=f"Row {ROW_ID}, once")
    psql(f"""insert into orders (id, customer_id, amount_cents, created, status)
select id, customer_id, amount_cents, created, status from orders where id = {ROW_ID};""",
         title="Insert it again, unchanged. Nothing stops this.")
    psql(f"select id, customer_id, amount_cents, status from orders where id = {ROW_ID};",
         title=f"Row {ROW_ID}, twice",
         note="Two rows, identical in every column. `id` was never promised to be unique.")

    data["dup_rows"] = int(one(f"select count(*) from orders where id = {ROW_ID}"))
    data["revenue_total_dup"] = int(one(
        "select sum(o.amount_cents) from customers c join orders o on o.customer_id = c.id "
        "where o.status = 'paid'"))
    data["dup_amount"] = int(one(f"select amount_cents from orders where id = {ROW_ID} limit 1"))
    data["dup_status"] = one(f"select status from orders where id = {ROW_ID} limit 1")
    data["dup_country"] = one(
        f"select c.country from customers c join orders o on o.customer_id = c.id "
        f"where o.id = {ROW_ID} limit 1")

    psql(QUESTION, title="The same question, the same word 'revenue', a different answer",
         note="One country's revenue moved. There are two order rows now, each matching the "
              "same customer, so that order's amount is added twice. Nothing errored, "
              "nothing in the query changed, and no row count looks wrong on its own.")

    # ---------------------------------------------------------------- 5. defend
    section("5. The constraint that would have stopped it")

    psql("alter table orders add primary key (id);",
         title="Try to declare what you meant all along", expect_error=True,
         note="The constraint cannot be added while the data already violates it. This is "
              "the usual order of events: the duplicate arrives first, the constraint second.")

    psql(f"""delete from orders o
where o.ctid <> (select min(i.ctid) from orders i where i.id = o.id)
  and o.id = {ROW_ID};""", title="Remove the duplicate, keeping one copy")
    psql("alter table orders add primary key (id);", title="Now it can be declared")
    psql(f"""insert into orders (id, customer_id, amount_cents, created, status)
select id, customer_id, amount_cents, created, status from orders where id = {ROW_ID};""",
         title="Insert the duplicate again", expect_error=True,
         note="Rejected by the server, in the server, for every client that will ever "
              "connect to it. That is the difference between a rule in your application "
              "and a rule in your database.")

    data["revenue_total_fixed"] = int(one(
        "select sum(o.amount_cents) from customers c join orders o on o.customer_id = c.id "
        "where o.status = 'paid'"))
    data["pk_index"] = one(
        "select indexrelid::regclass::text from pg_index "
        "where indrelid = 'orders'::regclass and indisprimary")

    psql("""select conname, contype, pg_get_constraintdef(oid) as definition
from pg_constraint where conrelid = 'orders'::regclass;""",
         title="The constraint, as a row in the catalog",
         note="Declaring it also built an index: a primary key is enforced by a unique "
              "index, which is why the check costs nothing on lookup.")

    # ---------------------------------------------------------------- 6. surprise two
    section("6. The second surprise: NULL is not a value",
            "Both counts below count the same rows. They disagree because one of them is "
            "not counting rows.")

    psql(f"select count(*), count(amount_cents) from orders where id = {ROW_ID};",
         title="Before: the two counts agree")
    psql("alter table orders alter column amount_cents drop not null;",
         title="Drop the constraint that was preventing this",
         note="`amount_cents` was declared `not null` by shopgen. Removing it is a "
              "deliberate act, and it is the only reason the next statement works.")
    psql(f"update orders set amount_cents = null where id = {ROW_ID};",
         title="One amount is now unknown")
    psql("select count(*), count(amount_cents) from orders;",
         title="After: count(*) and count(amount_cents) differ by one",
         note="`count(*)` counts rows. `count(amount_cents)` counts rows where that column "
              "is not null. They were never the same function.")

    data["count_star"] = int(one("select count(*) from orders"))
    data["count_amount"] = int(one("select count(amount_cents) from orders"))
    data["sum_after_null"] = int(one("select sum(amount_cents) from orders"))

    psql(f"""select count(*) as rows_matching
from orders where amount_cents = null;""",
         title="And the row cannot be found by asking for it",
         note="`= null` is never true. It is not false either: it is unknown, and a WHERE "
              "clause keeps only rows for which the condition is true.")
    psql(f"""select count(*) as rows_matching
from orders where amount_cents is null;""",
         title="`is null` is the operator that asks the question")

    data["eq_null_rows"] = int(one("select count(*) from orders where amount_cents = null"))
    data["is_null_rows"] = int(one("select count(*) from orders where amount_cents is null"))

    psql("""select sum(amount_cents) as sum_ignores_null,
       avg(amount_cents)::numeric(12,2) as avg_ignores_null,
       count(*) as rows
from orders where status = 'paid';""",
         title="Every aggregate but count(*) skips the unknown",
         note="The average is over the rows that have an amount, not over the paid orders. "
              "Whether that is what you meant is a question SQL cannot ask you.")

    # ---------------------------------------------------------------- write
    CAP_MD.write_text("\n".join(md) + "\n")
    CAP_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {CAP_MD.name} ({CAP_MD.stat().st_size:,} B) and "
          f"{CAP_JSON.name} ({CAP_JSON.stat().st_size:,} B)")


if __name__ == "__main__":
    main()
