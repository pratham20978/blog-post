#!/usr/bin/env python3
"""check.py - marks your own run of the part 4 lab, one rung at a time.

Each rung has a self-check you could do by hand; this script does it for you and says
which number did not match. It reads the committed captures.json, so it is comparing your
server with the author's run, not with a number typed into this file.

    PGBIN=... PGSOCK=... python3 check.py e1     reproduce the revenue table
    PGBIN=... PGSOCK=... python3 check.py e2     inspect what the executor read
    PGBIN=... PGSOCK=... python3 check.py e3     predict the two counts, then check
    PGBIN=... PGSOCK=... python3 check.py e4 --break    inject the fault
    PGBIN=... PGSOCK=... python3 check.py e4 --verify   mark your fix

Run it against the shoplab database shopgen built, never anything else.
"""
import argparse
import json
import os
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
PGBIN = pathlib.Path(os.environ["PGBIN"])
SOCK = pathlib.Path(os.environ["PGSOCK"])
USER = os.environ.get("PGUSER", "postgres")
DB = "shoplab"
ROW_ID = 4242
CAP = json.loads((HERE / "captures.json").read_text())

QUESTION = """select c.country, sum(o.amount_cents), count(*)
from customers c join orders o on o.customer_id = c.id
where o.status = 'paid' group by c.country order by 2 desc"""

PASS, FAIL = "PASS", "FAIL"
results = []


def q(sql, expect_error=False):
    args = [str(PGBIN / "psql"), "-X", "-q", "-At", "-h", str(SOCK), "-U", USER, "-d", DB,
            "-P", "pager=off"]
    if not expect_error:
        args += ["-v", "ON_ERROR_STOP=1"]
    out = subprocess.run(args, input=sql, capture_output=True, text=True,
                         env=dict(os.environ, PGTZ="UTC"))
    if out.returncode != 0 and not expect_error:
        raise SystemExit(f"psql failed:\n{sql}\n{out.stderr}")
    return ((out.stdout or "") + (out.stderr or "")).strip()


def mark(label, ok, detail=""):
    results.append((label, ok))
    print(f"  [{PASS if ok else FAIL}] {label}" + (f"\n         {detail}" if detail else ""))


def e1():
    """Reproduce: the revenue table, to the cent."""
    print("E1 - reproduce the revenue table")
    got = [r.split("|") for r in q(QUESTION).splitlines()]
    want = CAP["revenue_clean"]
    mark("five countries, in the author's order",
         [r[0] for r in got] == [r[0] for r in want],
         f"got {[r[0] for r in got]}, author {[r[0] for r in want]}")
    mark("every revenue figure matches to the cent",
         [r[1] for r in got] == [r[1] for r in want],
         f"first mismatch: {next((f'{g[0]}: {g[1]} vs {w[1]}' for g, w in zip(got, want) if g[1] != w[1]), 'none')}")
    mark("paid order counts match",
         [r[2] for r in got] == [r[2] for r in want])
    print("  If these fail, shopgen ran at a scale other than M, or the fault from E4 is\n"
          "  still in place. Re-run shopgen.py --scale M --db shoplab --drop.")


def e2():
    """Inspect: what the executor actually read."""
    print("E2 - inspect what the executor read")
    plan = q(f"explain (analyze, buffers, timing off, summary off) {QUESTION}")
    m = re.search(r"Parallel Seq Scan on orders.*?Buffers: shared hit=(\d+)", plan, re.S)
    if not m:
        m = re.search(r"Seq Scan on orders.*?Buffers: shared (?:hit|read)=(\d+)", plan, re.S)
    hit = int(m.group(1)) if m else -1
    relpages = int(q("select relpages from pg_class where relname = 'orders'"))
    mark("the scan of orders read one buffer per page of orders",
         hit == relpages, f"buffers={hit}, pg_class.relpages={relpages}")
    mark("that page count is the one the series has published since part 1",
         relpages == CAP["orders_relpages"],
         f"got {relpages}, author {CAP['orders_relpages']}")
    print("  Buffers are in EXPLAIN ANALYZE by default from PostgreSQL 18. On 16 and 17 ask\n"
          "  for them: EXPLAIN (ANALYZE, BUFFERS).")


def e3():
    """Predict: what NULL does to the two counts."""
    print("E3 - predict the counts, then check")
    print("  Write your three predictions down before reading further:")
    print("    count(*), count(amount_cents), and whether sum() changes.")
    isnull = int(q("select count(*) from orders where amount_cents is null"))
    if isnull == 0:
        print("\n  No amount is null yet. Run this, then run check.py e3 again:")
        print("    alter table orders alter column amount_cents drop not null;")
        print(f"    update orders set amount_cents = null where id = {ROW_ID};")
        return
    star = int(q("select count(*) from orders"))
    amt = int(q("select count(amount_cents) from orders"))
    mark("count(*) counts every row, including the one with no amount",
         star == amt + isnull, f"count(*)={star}, count(amount_cents)={amt}, null rows={isnull}")
    mark("the two counts differ by exactly the number of null amounts",
         star - amt == isnull, f"difference={star - amt}, null rows={isnull}")
    mark("`= null` finds nothing, `is null` finds the row",
         int(q("select count(*) from orders where amount_cents = null")) == 0 and isnull > 0)
    print("  sum() skips the unknown rather than returning unknown, which is a choice SQL\n"
          "  made and the three-valued logic of WHERE does not make for you.")


def e4_break():
    """Diagnose: inject the fault."""
    print("E4 - injecting the fault")
    if q("select count(*) from pg_constraint where conrelid='orders'::regclass "
         "and contype='p'") != "0":
        raise SystemExit("  orders already has a primary key: the fault cannot be injected.\n"
                         "  Re-run shopgen.py --scale M --db shoplab --drop first.")
    if q("select count(*) from orders where amount_cents is null") != "0":
        raise SystemExit("  an amount is null (left by E3), so the fault would not show as a\n"
                         "  revenue change. Re-run shopgen.py --scale M --db shoplab --drop first.")
    q(f"""insert into orders (id, customer_id, amount_cents, created, status)
select id, customer_id, amount_cents, created, status from orders where id = {ROW_ID}""")
    print("  Done. One country's revenue is now wrong.\n"
          "  Find which, by how much, and why. Then make the server refuse the cause.\n"
          "  Mark yourself with: python3 check.py e4 --verify")


def e4_verify():
    """Diagnose: mark the fix."""
    print("E4 - marking your fix")
    total = int(q("select sum(o.amount_cents) from customers c "
                  "join orders o on o.customer_id = c.id where o.status = 'paid'"))
    mark("revenue is back to the E1 figure",
         total == CAP["revenue_total_clean"],
         f"got {total:,}, author {CAP['revenue_total_clean']:,}, "
         f"difference {total - CAP['revenue_total_clean']:,}")
    mark("only one row has that id again",
         int(q(f"select count(*) from orders where id = {ROW_ID}")) == 1)
    # The probe inserts one duplicate to see whether the server stops it. It returns its
    # own ctid so that, if the server did not stop it, exactly that row is removed again -
    # never the duplicate you were asked to diagnose.
    err = q(f"""insert into orders (id, customer_id, amount_cents, created, status)
select id, customer_id, amount_cents, created, status from orders where id = {ROW_ID}
limit 1 returning ctid""", expect_error=True)
    rejected = "duplicate key value violates unique constraint" in err
    mark("the server now rejects the duplicate itself", rejected,
         "the insert succeeded - deleting the row is not the fix, declaring the "
         "constraint is" if not rejected else err.splitlines()[0])
    if not rejected:
        probe_ctid = err.strip().splitlines()[0]
        q(f"delete from orders where ctid = '{probe_ctid}'::tid")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rung", choices=["e1", "e2", "e3", "e4"])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--break", dest="brk", action="store_true")
    g.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    if a.rung == "e4":
        if a.brk:
            e4_break()
        elif a.verify:
            e4_verify()
        else:
            raise SystemExit("e4 needs --break (inject the fault) or --verify (mark your fix)")
    else:
        {"e1": e1, "e2": e2, "e3": e3}[a.rung]()
    if results:
        bad = [l for l, ok in results if not ok]
        print(f"\n{len(results) - len(bad)}/{len(results)} checks passed"
              + (f"; look again at: {bad[0]}" if bad else ""))
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
