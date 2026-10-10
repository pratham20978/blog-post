#!/usr/bin/env python3
"""shopgen — the PostgreSQL Foundations shop dataset, built the same way every time.

Creates a throwaway database and loads the two tables the series has used since part 1:

    customers   id, name, country          fillfactor 90, primary key on id
    orders      id, customer_id, amount_cents, created, status   no primary key

The DDL is byte-for-byte the DDL parts 1-3 used, so a number captured on this lab lines up
with the numbers those posts published. Scale M is that compat scale: 100,000 customers and
1,000,000 orders. S is the same shape at a hundredth of the size, for a smaller disk.

    python3 shopgen.py --scale M --db shoplab

Part 5 added --orderless N: N more customers, numbered after the last one, who have placed no
order. Without it every customer has exactly 10 orders (7,919 is coprime to 100,000, so the
customer_id formula visits every customer once per 100,000 orders), and an outer join would
have nothing to add. Leave it off and scale M is unchanged, row for row.

    python3 shopgen.py --scale M --orderless 1000 --db shoplab

Point it at a throwaway cluster you started yourself. It refuses a database it did not
create unless you pass --drop, and it never contacts a server it was not given a socket for.
"""
import argparse
import os
import pathlib
import subprocess
import sys
import time

SCALES = {"S": (1_000, 10_000), "M": (100_000, 1_000_000), "L": (1_000_000, 10_000_000)}
STAMP = "shopgen"

# The exact DDL parts 1-3 used. Do not reformat: the page counts depend on it.
SCHEMA = """create table customers (
    id       int primary key,
    name     text not null,
    country  char(2) not null
) with (fillfactor = 90);
insert into customers
select g, 'customer ' || g, (array['IN','US','DE','BR','JP'])[1 + g % 5]
from generate_series(1, {customers}) g;

create table orders (
    id           int not null,
    customer_id  int not null,
    amount_cents int not null,
    created      timestamptz not null,
    status       text not null
);
insert into orders
select g,
       1 + (g::bigint * 7919) % {customers},
       (g::bigint * 37) % 100000,
       timestamptz '2026-01-01 00:00:00+00' + (g % 86400) * interval '1 second',
       (array['paid','shipped','refunded'])[1 + g % 3]
from generate_series(1, {orders}) g;
"""

# Customers with no orders, numbered after the last generated customer, by the same rules.
ORDERLESS = """insert into customers
select g, 'customer ' || g, (array['IN','US','DE','BR','JP'])[1 + g % 5]
from generate_series({first}, {last}) g;
"""

INDEXES = """create index orders_customer_idx on orders (customer_id);
create index orders_created_idx  on orders (created);
"""


def psql(sql, db, bin_dir, sock, user, quiet=True):
    args = [str(bin_dir / "psql"), "-X", "-q", "-h", str(sock), "-U", user, "-d", db,
            "-P", "pager=off", "-v", "ON_ERROR_STOP=1"]
    if quiet:
        args += ["-At"]
    out = subprocess.run(args, input=sql, capture_output=True, text=True,
                         env=dict(os.environ, PGTZ="UTC"))
    if out.returncode != 0:
        raise SystemExit(f"psql failed:\n{sql}\n{out.stderr}")
    return out.stdout.rstrip("\n")


def main():
    p = argparse.ArgumentParser(description="generate the series shop dataset")
    p.add_argument("--scale", default="M", choices=sorted(SCALES))
    p.add_argument("--db", default="shoplab")
    p.add_argument("--indexes", action="store_true",
                   help="also create part 2's two indexes on orders")
    p.add_argument("--orderless", type=int, default=0, metavar="N",
                   help="add N customers who have placed no order (part 5 uses 1000)")
    p.add_argument("--drop", action="store_true",
                   help="drop the target database first if it already exists")
    p.add_argument("--bin", default=os.environ.get("PGBIN"),
                   help="the bin/ of the server you started (or set PGBIN)")
    p.add_argument("--sock", default=os.environ.get("PGSOCK"),
                   help="its unix socket directory (or set PGSOCK)")
    p.add_argument("--user", default=os.environ.get("PGUSER", "postgres"))
    a = p.parse_args()
    if not a.bin or not a.sock:
        raise SystemExit("set PGBIN and PGSOCK (or pass --bin and --sock): this lab only ever "
                         "talks to a server you started yourself")
    bin_dir, sock = pathlib.Path(a.bin), pathlib.Path(a.sock)

    exists = psql(f"select 1 from pg_database where datname = '{a.db}'",
                  "postgres", bin_dir, sock, a.user) == "1"
    if exists:
        # Refuse a database this script did not create: it may be something you care about.
        mine = psql(f"select shobj_description(oid, 'pg_database') from pg_database "
                    f"where datname = '{a.db}'", "postgres", bin_dir, sock, a.user)
        if mine != STAMP and not a.drop:
            raise SystemExit(f"database {a.db} exists and was not created by shopgen. "
                             f"Pass --drop only if you are certain it is disposable.")
        psql(f'drop database "{a.db}"', "postgres", bin_dir, sock, a.user)

    customers, orders = SCALES[a.scale]
    psql(f'create database "{a.db}"', "postgres", bin_dir, sock, a.user)
    psql(f"comment on database \"{a.db}\" is '{STAMP}'", "postgres", bin_dir, sock, a.user)

    t0 = time.time()
    psql(SCHEMA.format(customers=customers, orders=orders), a.db, bin_dir, sock, a.user)
    if a.orderless > 0:
        psql(ORDERLESS.format(first=customers + 1, last=customers + a.orderless),
             a.db, bin_dir, sock, a.user)
    if a.indexes:
        psql(INDEXES, a.db, bin_dir, sock, a.user)
    psql("vacuum analyze customers;\nvacuum analyze orders;", a.db, bin_dir, sock, a.user)
    load = time.time() - t0

    sizes = psql("""select relname || ' ' || relpages || ' ' || reltuples::bigint
                    from pg_class where relname in ('customers','orders')
                    order by relname""", a.db, bin_dir, sock, a.user)
    extra = f" (+{a.orderless:,} with no orders)" if a.orderless > 0 else ""
    print(f"shopgen scale {a.scale}: {customers:,} customers{extra}, {orders:,} orders "
          f"into {a.db} in {load:.1f}s")
    for line in sizes.splitlines():
        name, pages, tuples = line.split()
        print(f"  {name:<10} {int(pages):>8,} pages  {int(tuples):>10,} rows")


if __name__ == "__main__":
    main()
