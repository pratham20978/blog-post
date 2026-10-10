#!/usr/bin/env python3
"""check.py - marks your own run of the part 5 lab, one rung at a time.

Each rung has a self-check you could do by hand; this script does it for you and says which
number did not match. It reads the committed captures.json, so it compares your server with
the author's run, not with a number typed into this file.

    PGBIN=... PGSOCK=... python3 check.py e1                    reproduce the report's row counts
    PGBIN=... PGSOCK=... python3 check.py e2                    inspect where HAVING was applied
    PGBIN=... PGSOCK=... python3 check.py e3 --predict 1,3,6    predict which of six queries change
    PGBIN=... PGSOCK=... python3 check.py e4 --break            inject the fault
    PGBIN=... PGSOCK=... python3 check.py e4 --verify           mark your repairs in fixed.sql

Run it against the shoplab database shopgen built, never anything else. Start each rung from
fresh data: python3 shopgen.py --scale M --orderless 1000 --db shoplab --drop
"""
import argparse
import json
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
PGBIN = pathlib.Path(os.environ["PGBIN"])
SOCK = pathlib.Path(os.environ["PGSOCK"])
USER = os.environ.get("PGUSER", "postgres")
DB = "shoplab"
ROW_ID = 4242
CAP = json.loads((HERE / "captures.json").read_text())
FULL = CAP["full"]
# NOT IN over 1,000,000 rows takes minutes at the default work_mem (the article says why).
# This script raises work_mem for its own sessions only; the answers do not depend on it.
FAST = "set work_mem = '64MB';\n"
NULL_MARK = "<null>"

SIX = {
    1: ("rows after customers JOIN orders",
        "select count(*) from customers c join orders o on o.customer_id = c.id"),
    2: ("customers whose id is IN the orders' customer_ids",
        "select count(*) from customers where id in (select customer_id from orders)"),
    3: ("customers whose id is NOT IN the orders' customer_ids",
        "select count(*) from customers where id not in (select customer_id from orders)"),
    4: ("customers for whom NOT EXISTS an order",
        "select count(*) from customers c "
        "where not exists (select 1 from orders o where o.customer_id = c.id)"),
    5: ("count(DISTINCT customer_id) in orders",
        "select count(distinct customer_id) from orders"),
    6: ("groups after GROUP BY customer_id",
        "select count(*) from (select customer_id from orders group by customer_id) g"),
}

PASS, FAIL = "PASS", "FAIL"
results = []


def q(sql, expect_error=False):
    args = [str(PGBIN / "psql"), "-X", "-q", "-At", "-P", f"null={NULL_MARK}",
            "-h", str(SOCK), "-U", USER, "-d", DB, "-P", "pager=off"]
    if not expect_error:
        args += ["-v", "ON_ERROR_STOP=1"]
    out = subprocess.run(args, input=sql, capture_output=True, text=True,
                         env=dict(os.environ, PGTZ="UTC"))
    if out.returncode != 0 and not expect_error:
        raise SystemExit(f"psql failed:\n{sql}\n{out.stderr}")
    return ((out.stdout or "") + (out.stderr or "")).strip()


def rows(sql):
    out = []
    for line in q(sql).splitlines():
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


def mark(label, ok, detail=""):
    results.append((label, ok))
    print(f"  [{PASS if ok else FAIL}] {label}" + (f"\n         {detail}" if detail else ""))


def fresh():
    """True when the data is as shopgen left it: customer_id NOT NULL, no NULLs."""
    nullable = q("select not attnotnull from pg_attribute where attrelid = 'orders'::regclass "
                 "and attname = 'customer_id'") == "t"
    extra = int(q("select count(*) from customers where id > 100000"))
    return not nullable and extra == 1000


def e1():
    """Reproduce: the report's row count after every clause."""
    print("E1 - reproduce the report, clause by clause")
    steps = [
        ("FROM customers", "select count(*) from customers c", "customers"),
        ("... JOIN orders", "select count(*) from customers c join orders o "
                            "on o.customer_id = c.id", "inner_join"),
        ("... LEFT JOIN orders instead", "select count(*) from customers c left join orders o "
                                         "on o.customer_id = c.id", "left_join"),
        ("... WHERE o.status = 'paid'", "select count(*) from customers c join orders o "
                                        "on o.customer_id = c.id where o.status = 'paid'",
         "where_paid"),
        ("... GROUP BY c.country", "select count(*) from (select c.country from customers c "
                                   "join orders o on o.customer_id = c.id "
                                   "where o.status = 'paid' group by c.country) g", "groups"),
    ]
    for label, sql, key in steps:
        got = int(q(sql))
        mark(f"{label}: {FULL[key]:,} rows", got == FULL[key], f"got {got:,}")
    report = rows("""select c.country, count(*), sum(o.amount_cents)
from customers c join orders o on o.customer_id = c.id
where o.status = 'paid' group by c.country order by 3 desc, 1""")
    want = sorted(FULL["report_ordered"], key=lambda r: (-r[2], r[0]))
    mark("the five paid-revenue rows match to the cent", report == want,
         f"first mismatch: {next((f'{g} vs {w}' for g, w in zip(report, want) if g != w), 'none')}")
    ties = rows("""select c.country from customers c join orders o on o.customer_id = c.id
where o.status = 'paid' group by c.country order by sum(o.amount_cents) desc
fetch first 2 rows with ties""")
    mark("FETCH FIRST 2 ROWS WITH TIES returns 3 rows: DE, IN and JP",
         sorted(r[0] for r in ties) == ["DE", "IN", "JP"], f"got {[r[0] for r in ties]}")
    print("  If these fail, shopgen ran without --orderless 1000 or at a scale other than M,\n"
          "  or a later exercise has changed the data. Re-run shopgen.py with --drop.")


def find(node, pred, path=()):
    """Yield (node, ancestors) for every plan node that satisfies pred."""
    if pred(node):
        yield node, path
    for child in node.get("Plans", []):
        yield from find(child, pred, path + (node,))


def e2():
    """Inspect: where did PostgreSQL apply the HAVING condition?"""
    print("E2 - inspect where the HAVING condition ran")
    having = """select c.country, o.status, count(*) from customers c
join orders o on o.customer_id = c.id group by c.country, o.status having o.status = 'paid'"""
    where = """select c.country, o.status, count(*) from customers c
join orders o on o.customer_id = c.id where o.status = 'paid' group by c.country, o.status"""
    ph = json.loads(q(f"explain (costs off, format json) {having}"))[0]["Plan"]
    pw = json.loads(q(f"explain (costs off, format json) {where}"))[0]["Plan"]
    hits = list(find(ph, lambda n: "status" in n.get("Filter", "")))
    on_scan = [n for n, _ in hits if n.get("Relation Name") == "orders"]
    on_agg = [n for n, _ in hits if "Aggregate" in n["Node Type"]]
    mark("the condition is a Filter on the scan of orders", bool(on_scan),
         f"found it on: {[n['Node Type'] for n, _ in hits] or 'no node'}")
    mark("no aggregate node filters on it", not on_agg)
    mark("the plan is identical to the WHERE version's", ph == pw)
    print("  In psql: EXPLAIN (COSTS OFF) <the HAVING query>; look for the line\n"
          "  Filter: (status = 'paid'::text) and note which node it sits under.")


def e3(predict):
    """Predict: which of six queries change when one order loses its customer?"""
    print("E3 - predict which queries change")
    if not fresh():
        raise SystemExit("  The data is not fresh. Run shopgen.py --scale M --orderless 1000 "
                         "--db shoplab --drop first.")
    try:
        guess = {int(x) for x in predict.split(",") if x.strip()}
    except ValueError:
        raise SystemExit("  --predict takes query numbers, for example --predict 2,4")
    before = {n: int(q(FAST + sql)) for n, (_, sql) in SIX.items()}
    q("alter table orders alter column customer_id drop not null;\n"
      f"update orders set customer_id = null where id = {ROW_ID};")
    after = {n: int(q(FAST + sql)) for n, (_, sql) in SIX.items()}
    changed = {n for n in SIX if before[n] != after[n]}
    for n, (label, _) in SIX.items():
        flag = "changed" if n in changed else "same"
        print(f"    {n}. {label:<55} {before[n]:>9,} -> {after[n]:>9,}  {flag}")
    mark("your prediction names exactly the queries that changed", guess == changed,
         f"you predicted {sorted(guess)}, the server changed {sorted(changed)}")
    mark("the author's run changed the same ones",
         sorted(changed) == sorted(int(k[1]) for k in FULL["six_changed"]))
    print("  The data now has a NULL in it. Run shopgen.py again before E4.")


def e4_break():
    print("E4 - injecting the fault")
    if not fresh():
        raise SystemExit("  The data is not fresh. Run shopgen.py --scale M --orderless 1000 "
                         "--db shoplab --drop first.")
    q("alter table orders alter column customer_id drop not null;\n"
      f"update orders set customer_id = null where id = {ROW_ID};")
    print("  Done. One order has lost its customer, as happens in real data.\n"
          "  Copy broken.sql to fixed.sql, repair each of its three queries in place,\n"
          "  and mark yourself with: python3 check.py e4 --verify")


def split_queries(path):
    parts, current, key = {}, [], None
    for line in path.read_text().splitlines():
        if line[:5] in ("-- A.", "-- B.", "-- C."):
            if key:
                parts[key] = "\n".join(current).strip()
            key, current = line[3], []
        elif key and not line.startswith("--"):
            current.append(line)
    if key:
        parts[key] = "\n".join(current).strip()
    return {k: v.rstrip(";") for k, v in parts.items()}


def e4_verify():
    print("E4 - marking fixed.sql")
    path = HERE / "fixed.sql"
    if not path.exists():
        raise SystemExit("  No fixed.sql here. Copy broken.sql to fixed.sql and repair it.")
    if q(f"select count(*) from orders where id = {ROW_ID} and customer_id is null") != "1":
        raise SystemExit("  The fault is not in place. Run check.py e4 --break on fresh data.")
    mine = split_queries(path)
    want = FULL["e4_reference"]
    labels = {"A": "A, paid and refunded revenue per country",
              "B": "B, customers who have never ordered",
              "C": "C, orders of at least 90,000 cents per country"}
    for k in ("A", "B", "C"):
        if k not in mine:
            mark(labels[k], False, f"no query found after the line '-- {k}.'")
            continue
        got = rows(FAST + mine[k])
        mark(labels[k], sorted(map(str, got)) == sorted(map(str, want[k])),
             f"got {got[:5]}{' ...' if len(got) > 5 else ''}, want {want[k]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rung", choices=["e1", "e2", "e3", "e4"])
    ap.add_argument("--predict", help="E3: the numbers of the queries you predict will change")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--break", dest="brk", action="store_true")
    g.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    if a.rung == "e3":
        if a.predict is None:
            print("E3 - write your prediction before you run anything. The six queries:")
            for n, (label, sql) in SIX.items():
                print(f"  {n}. {label}\n     {sql}")
            print("\n  Which of them return a different number after this?\n"
                  "    alter table orders alter column customer_id drop not null;\n"
                  f"    update orders set customer_id = null where id = {ROW_ID};\n"
                  "  Then run: python3 check.py e3 --predict <numbers>, for example 2,5")
            return
        e3(a.predict)
    elif a.rung == "e4":
        if a.brk:
            e4_break()
        elif a.verify:
            e4_verify()
        else:
            raise SystemExit("e4 needs --break (inject the fault) or --verify (mark fixed.sql)")
    else:
        {"e1": e1, "e2": e2}[a.rung]()
    if results:
        bad = [label for label, ok in results if not ok]
        print(f"\n{len(results) - len(bad)}/{len(results)} checks passed"
              + (f"; look again at: {bad[0]}" if bad else ""))
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
