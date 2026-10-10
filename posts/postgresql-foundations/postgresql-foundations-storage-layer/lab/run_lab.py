#!/usr/bin/env python3
"""Reproducible lab for "How PostgreSQL Stores Data" (postgresql-foundations, part 3).

Every number quoted in blog.md that came from a running server came from this script.
It drives a stock PostgreSQL 16.2 (the `pgserver` wheel's bundled binaries) with the
default postgresql.conf, on a data directory that lives on a real disk (not tmpfs), and
writes two files next to itself:

    captures.md    the psql output of every step, verbatim, in run order
    captures.json  the numbers the figures are drawn from

The two tables are byte-for-byte the ones parts 1 and 2 used (`customers`, 710 pages;
`orders`, 7,693 pages) plus part 2's two indexes on `orders`, so the series' numbers line
up. Part 3 follows one row of `orders` (id 4242) through two updates, a vacuum, a wide
value, an index lookup and a crash.

Two steps change the server and put it back: step 11 stops the server with
`pg_ctl stop -m immediate` (a simulated crash) and restarts it, and step 12 turns on WAL
archiving with ALTER SYSTEM, restarts, then resets both settings and restarts again.
Step 13 attaches pg_receivewal for three seconds, which makes the postmaster fork a
walsender.
Run this against a throwaway cluster, never a real one.

Needs the contrib modules pageinspect, pg_visibility, pg_freespacemap, pg_walinspect
and pg_buffercache.

Run:  PGBIN=/path/to/bin PGDATA=/path/to/pgdata PGSOCK=/path/to/sock python3 run_lab.py
"""
import datetime as dt
import json
import os
import pathlib
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time

import psycopg

HERE = pathlib.Path(__file__).resolve().parent
PGBIN = pathlib.Path(os.environ["PGBIN"])
PGDATA = pathlib.Path(os.environ["PGDATA"]).resolve()
SOCK = pathlib.Path(os.environ.get("PGSOCK", PGDATA.parent / "sock")).resolve()
DB = "storelab"
USER = "postgres"
BLCKSZ = 8192
WAL_SEG = 16 * 1024 * 1024
WAL_BLCKSZ = 8192
ROW_ID = 4242

CAP_MD = HERE / "captures.md"
CAP_JSON = HERE / "captures.json"
md = []
data = {}
ENV = dict(os.environ, PGTZ="UTC")


# --------------------------------------------------------------------------- plumbing
def pg_ctl(*args):
    return subprocess.run([str(PGBIN / "pg_ctl"), "-D", str(PGDATA), *args],
                          check=True, capture_output=True, text=True)


def start_server():
    pg_ctl("-w", "-o", '-h ""', "-o", f"-k {SOCK}", "-l", str(PGDATA / "server.log"), "start")
    time.sleep(0.5)


def restart_server():
    pg_ctl("-w", "-m", "fast", "stop")
    start_server()


def dsn(db=DB):
    return f"host={SOCK} user={USER} dbname={db} options='-c timezone=UTC'"


def psql(sql, db=DB, title=None, note=None, record=True, stderr=False):
    """Run SQL through psql and keep its text output, exactly as a reader would see it."""
    out = subprocess.run([str(PGBIN / "psql"), "-X", "-q", "-h", str(SOCK), "-U", USER, "-d", db,
                          "-P", "pager=off", "-v", "ON_ERROR_STOP=1"],
                         input=sql, capture_output=True, text=True, env=ENV)
    if out.returncode != 0:
        raise RuntimeError(f"psql failed:\n{sql}\n{out.stderr}")
    text = (out.stdout + out.stderr) if stderr else out.stdout
    text = text.rstrip("\n")
    if record:
        md.append(f"### {title}\n" if title else "")
        if note:
            md.append(note + "\n")
        md.append("```sql\n" + sql.strip() + "\n```\n")
        md.append("```text\n" + text + "\n```\n")
    return text


def q(sql, db=DB, params=None):
    with psycopg.connect(dsn(db), autocommit=True) as c:
        return c.execute(sql, params).fetchall()


def q1(sql, db=DB, params=None):
    return q(sql, db, params)[0][0]


def section(title, blurb=None):
    md.append(f"\n## {title}\n")
    if blurb:
        md.append(blurb + "\n")


def block(text, lang="text"):
    md.append(f"```{lang}\n{text}\n```\n")


def say(text):
    md.append(text + "\n")


def log_offset():
    return (PGDATA / "server.log").stat().st_size


def log_since(off):
    with open(PGDATA / "server.log", "rb") as f:
        f.seek(off)
        return f.read().decode(errors="replace")


def postmaster_pid():
    return int((PGDATA / "postmaster.pid").read_text().splitlines()[0])


def ps_children():
    pm = postmaster_pid()
    out = subprocess.run(["ps", "-o", "pid=,args=", "--ppid", str(pm)],
                         capture_output=True, text=True).stdout
    return "\n".join(l.strip() for l in out.splitlines() if l.strip())


def controldata(keys=None):
    out = subprocess.run([str(PGBIN / "pg_controldata"), str(PGDATA)],
                         capture_output=True, text=True, check=True).stdout
    rows = dict(l.split(":", 1) for l in out.splitlines() if ":" in l)
    rows = {k.strip(): v.strip() for k, v in rows.items()}
    if keys:
        rows = {k: rows[k] for k in keys}
    return rows


def lsn_int(lsn):
    hi, lo = lsn.split("/")
    return (int(hi, 16) << 32) | int(lo, 16)


def lsn_str(v):
    return f"{v >> 32:X}/{v & 0xFFFFFFFF:08X}"


# --------------------------------------------------------------------------- byte decoders
def decode_page_header(raw):
    xlogid, xrecoff, chk, flags, lower, upper, special, psv, prune = struct.unpack_from(
        "<IIHHHHHHI", raw, 0)
    return {"pd_lsn": f"{xlogid:X}/{xrecoff:08X}", "pd_checksum": chk, "pd_flags": flags,
            "pd_lower": lower, "pd_upper": upper, "pd_special": special,
            "page_size": psv & 0xFF00, "layout_version": psv & 0x00FF, "pd_prune_xid": prune}


def decode_line_pointer(raw, lp):
    v = struct.unpack_from("<I", raw, 24 + 4 * (lp - 1))[0]
    return {"lp": lp, "raw_hex": raw[24 + 4 * (lp - 1):28 + 4 * (lp - 1)].hex(),
            "lp_off": v & 0x7FFF, "lp_flags": (v >> 15) & 0x3, "lp_len": v >> 17}


def decode_tuple_header(tup):
    xmin, xmax, field3 = struct.unpack_from("<III", tup, 0)
    bi_hi, bi_lo, posid = struct.unpack_from("<HHH", tup, 12)
    im2, im, hoff = struct.unpack_from("<HHB", tup, 18)
    return {"t_xmin": xmin, "t_xmax": xmax, "t_field3": field3,
            "t_ctid": f"({(bi_hi << 16) | bi_lo},{posid})",
            "t_infomask2": im2, "natts": im2 & 0x07FF, "t_infomask": im, "t_hoff": hoff}


def decode_orders_data(d):
    """id int4 · customer_id int4 · amount_cents int4 · (pad to 8) · created timestamptz · status text"""
    ident, cust, amount = struct.unpack_from("<iii", d, 0)
    pad = d[12:16]
    created_us = struct.unpack_from("<q", d, 16)[0]
    created = dt.datetime(2000, 1, 1, tzinfo=dt.timezone.utc) + dt.timedelta(microseconds=created_us)
    hdr = d[24]
    assert hdr & 0x01, "expected a 1-byte varlena header"
    vlen = hdr >> 1
    status = d[25:24 + vlen].decode()
    return {"id": ident, "customer_id": cust, "amount_cents": amount, "pad_hex": pad.hex(),
            "created_us_since_2000": created_us, "created": created.isoformat(),
            "status_header_hex": f"{hdr:02x}", "status_total_len": vlen, "status": status,
            "data_len": 24 + vlen}


# CRC-32C (Castagnoli), the checksum PostgreSQL puts on every WAL record
_CRC_TABLE = []
for _i in range(256):
    _c = _i
    for _ in range(8):
        _c = (_c >> 1) ^ 0x82F63B78 if _c & 1 else _c >> 1
    _CRC_TABLE.append(_c)


def crc32c(buf):
    c = 0xFFFFFFFF
    for b in buf:
        c = _CRC_TABLE[(c ^ b) & 0xFF] ^ (c >> 8)
    return c ^ 0xFFFFFFFF


def read_wal_record(lsn):
    """Pull one record's bytes straight out of its segment file, stepping over WAL page headers."""
    v = lsn_int(lsn)
    segno = v // WAL_SEG
    fname = f"{1:08X}{segno // 256:08X}{segno % 256:08X}"
    path = PGDATA / "pg_wal" / fname
    buf = path.read_bytes()
    off = v % WAL_SEG
    tot_len = struct.unpack_from("<I", buf, off)[0]
    out = bytearray()
    pos = off
    while len(out) < tot_len:
        page_end = (pos // WAL_BLCKSZ + 1) * WAL_BLCKSZ
        take = min(tot_len - len(out), page_end - pos)
        out += buf[pos:pos + take]
        pos += take
        if len(out) < tot_len:          # continued on the next WAL page, after its header
            hdr = 40 if pos % WAL_SEG == 0 else 24
            pos += hdr
    return fname, off, bytes(out)


def decode_wal_record(rec):
    tot_len, xid, prev, info, rmid, crc = struct.unpack_from("<IIQBBxxI", rec, 0)
    computed = crc32c(rec[24:] + rec[:20])
    parts = [("XLogRecord header", 0, 24)]
    pos, blocks, main_len = 24, [], 0
    datalens = []
    while pos < tot_len:
        bid = rec[pos]
        if bid == 255:                  # XLR_BLOCK_ID_DATA_SHORT
            main_len = rec[pos + 1]
            parts.append(("main-data header (short)", pos, 2))
            pos += 2
            break
        if bid == 254:                  # XLR_BLOCK_ID_DATA_LONG
            main_len = struct.unpack_from("<I", rec, pos + 1)[0]
            parts.append(("main-data header (long)", pos, 5))
            pos += 5
            break
        if bid == 253:                  # XLR_BLOCK_ID_ORIGIN
            parts.append(("origin", pos, 3)); pos += 3; continue
        if bid == 252:                  # XLR_BLOCK_ID_TOPLEVEL_XID
            parts.append(("top-level xid", pos, 5)); pos += 5; continue
        fork_flags, dlen = struct.unpack_from("<BH", rec, pos + 1)
        start = pos
        pos += 4
        has_image = bool(fork_flags & 0x10)
        same_rel = bool(fork_flags & 0x80)
        img_len = 0
        if has_image:
            img_len, hole_off, bimg_info = struct.unpack_from("<HHB", rec, pos)
            pos += 5
            if bimg_info & 0x01 and bimg_info & 0x1C:         # hole in a compressed image
                pos += 2                                       # XLogRecordBlockCompressHeader
        rel = None
        if not same_rel:
            rel = struct.unpack_from("<III", rec, pos)
            pos += 12
        blkno = struct.unpack_from("<I", rec, pos)[0]
        pos += 4
        parts.append((f"block {bid} header", start, pos - start))
        blocks.append({"id": bid, "fork_flags": fork_flags, "data_length": dlen,
                       "has_image": has_image, "image_length": img_len,
                       "rel": list(rel) if rel else None, "block": blkno})
        datalens.append((bid, img_len, dlen))
    for bid, img_len, dlen in datalens:
        if img_len:
            parts.append((f"block {bid} image", pos, img_len)); pos += img_len
        if dlen:
            parts.append((f"block {bid} data", pos, dlen)); pos += dlen
    if main_len:
        parts.append(("main data", pos, main_len)); pos += main_len
    return {"xl_tot_len": tot_len, "xl_xid": xid, "xl_prev": lsn_str(prev), "xl_info": info,
            "xl_rmid": rmid, "xl_crc": f"{crc:08x}", "crc_computed": f"{computed:08x}",
            "crc_ok": crc == computed, "blocks": blocks, "main_data_length": main_len,
            "layout": [{"part": n, "offset": o, "length": l} for n, o, l in parts],
            "parsed_to": pos}


def wal_records(start, end, title, note=None):
    text = psql(f"""select start_lsn, end_lsn, xid, resource_manager as rmgr, record_type,
       record_length as len, fpi_length as fpi, block_ref
from pg_get_wal_records_info('{start}', '{end}');""", title=title, note=note)
    rows = q(f"""select start_lsn::text, end_lsn::text, xid::text, resource_manager, record_type,
        record_length, main_data_length, fpi_length, description, block_ref
        from pg_get_wal_records_info('{start}', '{end}')""")
    keys = ["start_lsn", "end_lsn", "xid", "rmgr", "record_type", "record_length",
            "main_data_length", "fpi_length", "description", "block_ref"]
    return [dict(zip(keys, r)) for r in rows]


def flush_lsn():
    time.sleep(0.4)                     # let the WAL writer flush records no commit waited for
    return q1("select pg_current_wal_flush_lsn()::text")


def raw_page(rel, blk, fork="main"):
    return bytes(q1(f"select get_raw_page('{rel}', '{fork}', {blk})"))


def disk_page(rel, blk):
    path = PGDATA / q1(f"select pg_relation_filepath('{rel}')")
    with open(path, "rb") as f:
        f.seek(blk * BLCKSZ)
        return f.read(BLCKSZ)


def items(rel, blk, where=""):
    return q(f"""select lp, lp_off, lp_flags, lp_len, t_xmin::text, t_xmax::text, t_ctid::text,
        t_infomask2, t_infomask,
        (select raw_flags from heap_tuple_infomask_flags(t_infomask, t_infomask2))::text
        from heap_page_items(get_raw_page('{rel}', {blk})) {where} order by lp""")


ITEM_KEYS = ["lp", "lp_off", "lp_flags", "lp_len", "t_xmin", "t_xmax", "t_ctid",
             "t_infomask2", "t_infomask", "flags"]


def items_json(rel, blk, where=""):
    return [dict(zip(ITEM_KEYS, r)) for r in items(rel, blk, where)]


def items_sql(rel, blk, where):
    return f"""select lp, lp_off, lp_flags, lp_len, t_xmin, t_xmax, t_ctid, t_infomask2, t_infomask,
       (select raw_flags from heap_tuple_infomask_flags(t_infomask, t_infomask2)) as flags
from heap_page_items(get_raw_page('{rel}', {blk}))
{where};"""


def hot_counters():
    return q("""select n_tup_upd, n_tup_hot_upd, n_dead_tup from pg_stat_user_tables
                where relname = 'orders'""")[0]


def checkpoints_so_far():
    return q1("select checkpoints_timed + checkpoints_req from pg_stat_bgwriter")


# =========================================================================== 0. fresh database
md.append("# Lab captures — How PostgreSQL Stores Data\n")
md.append("Generated by `run_lab.py`. PostgreSQL 16.2, default `postgresql.conf` except where a "
          "step says otherwise. Every psql session runs with `timezone = UTC`.\n")

if not (PGDATA / "postmaster.pid").exists():
    start_server()

assert "archive_mode" not in (PGDATA / "postgresql.auto.conf").read_text(), \
    "postgresql.auto.conf is not clean; reset it before running the lab"

psql(f"drop database if exists {DB};", db="postgres", record=False)
psql(f"create database {DB};", db="postgres", record=False)
psql("""create extension pageinspect; create extension pg_visibility;
create extension pg_freespacemap; create extension pg_walinspect;
create extension pg_buffercache;""", record=False)

machine = {
    "cpu": subprocess.run(["nproc"], capture_output=True, text=True).stdout.strip(),
    "mem_mb": int(re.search(r"MemTotal:\s+(\d+)", open("/proc/meminfo").read()).group(1)) // 1024,
    "disk": "Samsung NVMe (MZVL8512HELU), ext4",
    "kernel": os.uname().release,
}
data["machine"] = machine
data["version"] = q1("select version()")
data["run_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
md.append(f"Machine: {machine['cpu']} CPUs, {machine['mem_mb']} MB RAM, {machine['disk']}, "
          f"Linux {machine['kernel']}. Run {data['run_at']}.\n")
md.append(f"Server: `{data['version']}`\n")

psql("""select name, setting, unit
from pg_settings
where name in ('block_size','wal_block_size','wal_segment_size','segment_size',
               'data_checksums','wal_log_hints','full_page_writes','wal_level',
               'archive_mode','archive_command','max_wal_senders','checkpoint_timeout',
               'max_wal_size','default_toast_compression','wal_compression',
               'shared_buffers','autovacuum')
order by name;""", title="The storage-layer settings this lab runs with")
data["settings"] = {r[0]: r[1] for r in q("select name, setting from pg_settings")}

section("0. A checkpoint before anything else",
        "The first change to a page after a checkpoint carries a full-page image (part 1). "
        "Taking one now, before the load, means every page the load creates is born after "
        "it — so the two updates in steps 3 and 4 log only their own changes.")
psql("checkpoint;", record=False)
data["checkpoints_at_start"] = checkpoints_so_far()
t_lab0 = time.time()

# =========================================================================== 1. the tables
section("1. The same two tables parts 1 and 2 used, and every file they own")
psql("""create table customers (
    id       int primary key,
    name     text not null,
    country  char(2) not null
) with (fillfactor = 90);
insert into customers
select g, 'customer ' || g, (array['IN','US','DE','BR','JP'])[1 + g % 5]
from generate_series(1, 100000) g;

create table orders (
    id           int not null,
    customer_id  int not null,
    amount_cents int not null,
    created      timestamptz not null,
    status       text not null
);
insert into orders
select g,
       1 + (g::bigint * 7919) % 100000,
       (g::bigint * 37) % 100000,
       timestamptz '2026-01-01 00:00:00+00' + (g % 86400) * interval '1 second',
       (array['paid','shipped','refunded'])[1 + g % 3]
from generate_series(1, 1000000) g;

create index orders_customer_idx on orders (customer_id);
create index orders_created_idx  on orders (created);

vacuum analyze customers;
vacuum analyze orders;""", title="Schema and load (identical to parts 1 and 2)")

psql("""select c.relname, c.relkind, c.relfilenode, pg_relation_filepath(c.oid) as path,
       pg_relation_size(c.oid, 'main') / 8192 as main_pages,
       pg_relation_size(c.oid, 'fsm')  as fsm_bytes,
       pg_relation_size(c.oid, 'vm')   as vm_bytes
from pg_class c
where c.relname in ('orders','orders_customer_idx','orders_created_idx')
   or c.oid = (select reltoastrelid from pg_class where relname = 'orders')
   or c.oid = (select i.indexrelid from pg_index i
               where i.indrelid = (select reltoastrelid from pg_class where relname = 'orders'))
order by c.relkind desc, c.relname;""", title="Every relation behind `orders`, with its forks")
files = {}
for rel in ("orders", "orders_customer_idx", "orders_created_idx"):
    base = PGDATA / q1(f"select pg_relation_filepath('{rel}')")
    files[rel] = {p.name: p.stat().st_size for p in sorted(base.parent.glob(base.name + "*"))
                  if re.fullmatch(re.escape(base.name) + r"(_fsm|_vm|\.\d+)?", p.name)}
toast_oid = q1("select reltoastrelid from pg_class where relname = 'orders'")
toast_name = q1(f"select relname from pg_class where oid = {toast_oid}")
toast_path = PGDATA / q1(f"select pg_relation_filepath({toast_oid})")
files[f"pg_toast.{toast_name}"] = {p.name: p.stat().st_size
                                   for p in sorted(toast_path.parent.glob(toast_path.name + "*"))}
data["files"] = files
data["relfilepath_orders"] = q1("select pg_relation_filepath('orders')")
data["toast_table"] = f"pg_toast.{toast_name}"
lines = [f"{rel:24s} {name:14s} {size:>12,d} bytes" for rel, fs in files.items() for name, size in fs.items()]
say("The files themselves, from `ls` on the data directory (sizes in bytes):")
block("\n".join(lines))
data["pages"] = {r[0]: r[1] for r in q("""select relname, pg_relation_size(oid) / 8192 from pg_class
    where relname in ('customers','customers_pkey','orders','orders_customer_idx','orders_created_idx')""")}
data["db_oid"] = q1(f"select oid from pg_database where datname = '{DB}'")
data["pg_wal"] = list(q("select count(*), sum(size) from pg_ls_waldir()")[0])

# =========================================================================== 2. one row, byte by byte
section("2. Row 4242, found by its ctid and read byte by byte")
psql(f"select ctid, * from orders where id = {ROW_ID};", title="Where the row lives")
ctid = q1(f"select ctid::text from orders where id = {ROW_ID}")
blk, lp = map(int, ctid.strip("()").split(","))
data["row_ctid"] = ctid
data["row_block"], data["row_lp"] = blk, lp

psql(f"select * from page_header(get_raw_page('orders', {blk}));", title=f"Page {blk}'s header, via pageinspect")
raw = raw_page("orders", blk)
data["page_header_hex"] = raw[:24].hex()
data["page_header"] = decode_page_header(raw)
say(f"The first 24 bytes of page {blk}, raw: `{raw[:24].hex(' ')}`")
block(json.dumps(data["page_header"], indent=2))
nlp = (data["page_header"]["pd_lower"] - 24) // 4
data["line_pointers_on_page"] = nlp
data["free_bytes_on_page"] = data["page_header"]["pd_upper"] - data["page_header"]["pd_lower"]
data["lp_first"] = decode_line_pointer(raw, 1)
data["lp_row"] = decode_line_pointer(raw, lp)
data["lp_last"] = decode_line_pointer(raw, nlp)
say(f"{nlp} line pointers (pd_lower {data['page_header']['pd_lower']} − 24, ÷ 4); "
    f"{data['free_bytes_on_page']} bytes free between pd_lower and pd_upper.")
block(json.dumps([data["lp_first"], data["lp_row"], data["lp_last"]], indent=2))

psql(items_sql("orders", blk, f"where lp in (1, {lp}, {nlp})").replace(
    "from heap_page_items", "from heap_page_items").replace(
    "(select raw_flags", "t_hoff, t_bits, t_data,\n       (select raw_flags"),
     title="The row's line pointer and tuple header, via heap_page_items")
tup = raw[data["lp_row"]["lp_off"]:data["lp_row"]["lp_off"] + data["lp_row"]["lp_len"]]
data["row_tuple_hex"] = tup.hex()
data["row_tuple_header"] = decode_tuple_header(tup)
data["row_tuple_data"] = decode_orders_data(tup[data["row_tuple_header"]["t_hoff"]:])
say(f"The tuple's {len(tup)} bytes, raw: `{tup.hex(' ')}`")
block(json.dumps({"header": data["row_tuple_header"], "data": data["row_tuple_data"]}, indent=2))

psql("""select relname, relpages, reltuples::bigint,
       round((reltuples / relpages)::numeric, 1) as rows_per_page
from pg_class where relname in ('orders','customers');""", title="Rows per page")

# column order: the same rows with the 8-byte column first
psql("""create table orders_packed as
select created, id, customer_id, amount_cents, status from orders;
select pg_relation_size('orders_packed') / 8192 as pages_packed,
       pg_relation_size('orders') / 8192 as pages_original;
select count(*) filter (where lower > 24) as pages_with_rows,
       count(*) filter (where lower = 0)  as never_initialised,
       max((lower - 24) / 4)              as most_rows_on_a_page
from generate_series(0, pg_relation_size('orders_packed') / 8192 - 1) b,
     page_header(get_raw_page('orders_packed', b::int));""",
     title="Does column order change the page count?",
     note="Same million rows, with the 8-byte `created` column moved first so no padding is needed before it. "
          "CREATE TABLE AS inserts in bulk, and 16 extends a relation several pages at a time for bulk inserts, "
          "so the last few pages may be allocated but never initialised.")
data["pages_packed"] = q1("select pg_relation_size('orders_packed') / 8192")
data["packed_breakdown"] = list(q("""select count(*) filter (where lower > 24), count(*) filter (where lower = 0),
    max((lower - 24) / 4) from generate_series(0, pg_relation_size('orders_packed') / 8192 - 1) b,
    page_header(get_raw_page('orders_packed', b::int))""")[0])
psql("drop table orders_packed;", record=False)

# =========================================================================== 3. update 1
section("3. Update 1: change the status (not an indexed column)")
psql("select * from pg_freespace('orders') where avail > 0;",
     title="Before the update: which pages does the free space map say have room?")
data["fsm_before"] = [list(r) for r in q("select blkno, avail from pg_freespace('orders') where avail > 0")]
last = data["pages"]["orders"] - 1
ph_last = decode_page_header(raw_page("orders", last))
data["last_page_header_before"] = ph_last

cp_before = checkpoints_so_far()
upd0 = hot_counters()
lsn0 = q1("select pg_current_wal_insert_lsn()::text")
out = psql(f"""select pg_stat_force_next_flush();
begin;
update orders set status = 'shipped' where id = {ROW_ID};
select pg_current_xact_id() as xid;
commit;""", title="The update")
lsn1 = flush_lsn()
data["update1"] = {"xid": int(re.search(r"^\s*(\d+)\s*$", out, re.M).group(1)),
                   "lsn_before": lsn0, "lsn_after": lsn1}

psql(items_sql("orders", blk, f"where lp = {lp}"),
     title=f"Page {blk}, read raw before anyone else touches it",
     note="`get_raw_page` copies the buffer; it does not prune and does not set hint bits.")
data["update1"]["old_version"] = items_json("orders", blk, f"where lp = {lp}")[0]
new_ctid = data["update1"]["old_version"]["t_ctid"]
nblk, nlp_ = map(int, new_ctid.strip("()").split(","))
data["update1"]["new_ctid"] = new_ctid
psql(items_sql("orders", nblk, f"where lp = {nlp_}"),
     title=f"Following t_ctid to the new version at {new_ctid}")
data["update1"]["new_version_before_read"] = items_json("orders", nblk, f"where lp = {nlp_}")[0]
data["update1"]["wal"] = wal_records(lsn0, lsn1, "The WAL this update wrote")
data["update1"]["wal_bytes"] = lsn_int(lsn1) - lsn_int(lsn0)
data["update1"]["counters_after"] = hot_counters()

# a reader arrives
lsn2 = q1("select pg_current_wal_insert_lsn()::text")
psql(f"select ctid, status from orders where id = {ROW_ID};",
     title="A reader: a sequential scan that passes through both pages",
     note="There is no index on `id`, so this reads all 7,693 pages.")
lsn3 = flush_lsn()
psql(items_sql("orders", blk, f"where lp = {lp}") + "\n" +
     f"select lower, upper, flags, prune_xid from page_header(get_raw_page('orders', {blk}));",
     title=f"Page {blk} after the reader: the old version is pruned")
data["update1"]["old_after_reader"] = items_json("orders", blk, f"where lp = {lp}")[0]
data["update1"]["old_page_after_reader"] = decode_page_header(raw_page("orders", blk))
psql(items_sql("orders", nblk, f"where lp = {nlp_}"),
     title="The new version after the reader: hint bits now set")
data["update1"]["new_version_after_read"] = items_json("orders", nblk, f"where lp = {nlp_}")[0]
data["reader_wal"] = wal_records(lsn2, lsn3, "The WAL the reader wrote")

# =========================================================================== 4. update 2
section("4. Update 2: change the status again")
lsn4 = q1("select pg_current_wal_insert_lsn()::text")
out = psql(f"""select pg_stat_force_next_flush();
begin;
update orders set status = 'refunded' where id = {ROW_ID};
select pg_current_xact_id() as xid;
commit;""", title="The update")
lsn5 = flush_lsn()
data["update2"] = {"xid": int(re.search(r"^\s*(\d+)\s*$", out, re.M).group(1)),
                   "lsn_before": lsn4, "lsn_after": lsn5}
psql(items_sql("orders", nblk, f"where lp >= {nlp_}"), title=f"Page {nblk} after update 2")
data["update2"]["page_items"] = items_json("orders", nblk, f"where lp >= {nlp_}")
data["update2"]["wal"] = wal_records(lsn4, lsn5, "The WAL this update wrote")
data["update2"]["wal_bytes"] = lsn_int(lsn5) - lsn_int(lsn4)
time.sleep(0.6)
data["update2"]["counters_after"] = hot_counters()
psql("select n_tup_upd, n_tup_hot_upd, n_dead_tup from pg_stat_user_tables where relname = 'orders';",
     title="HOT counters")
cp_after = checkpoints_so_far()
data["checkpoints_during_updates"] = cp_after - cp_before
say(f"Checkpoints between the start of step 3 and here: {cp_after - cp_before} "
    "(0 means neither update carried a full-page image).")

# the record, located by LSN in its segment file and decoded by hand
upd2_heap = [r for r in data["update2"]["wal"] if r["rmgr"] == "Heap"][0]
fname, seg_off, rec = read_wal_record(upd2_heap["start_lsn"])
dec = decode_wal_record(rec)
data["update2"]["record_file"] = {"lsn": upd2_heap["start_lsn"], "segment_file": fname,
                                  "offset_in_segment": seg_off,
                                  "wal_page_in_segment": seg_off // WAL_BLCKSZ,
                                  "offset_in_wal_page": seg_off % WAL_BLCKSZ,
                                  "bytes_hex": rec.hex(), "decoded": dec}
psql(f"select * from pg_walfile_name_offset('{upd2_heap['start_lsn']}');",
     title="Which segment file holds the HOT_UPDATE record?")
say(f"Read {len(rec)} bytes from `pg_wal/{fname}` at offset {seg_off:,} "
    f"(WAL page {seg_off // WAL_BLCKSZ}, byte {seg_off % WAL_BLCKSZ} of that page):")
block(rec.hex(" "))
block(json.dumps(dec, indent=2))
wd = subprocess.run([str(PGBIN / "pg_waldump"), "-p", str(PGDATA / "pg_wal"),
                     "-s", lsn4, "-e", lsn5], capture_output=True, text=True)
data["update2"]["pg_waldump"] = wd.stdout.strip()
say("`pg_waldump` on the same range:")
block(wd.stdout.strip() + ("\n" + wd.stderr.strip() if wd.stderr.strip() else ""))

# segment file header
seg_bytes = (PGDATA / "pg_wal" / fname).read_bytes()[:40]
magic, info, tli, pageaddr, remlen, sysid, segsize, blcksz = struct.unpack_from("<HHIQI4xQII", seg_bytes, 0)
data["segment_header"] = {"file": fname, "hex": seg_bytes.hex(), "xlp_magic": f"0x{magic:04X}",
                          "xlp_info": info, "xlp_tli": tli, "xlp_pageaddr": lsn_str(pageaddr),
                          "xlp_rem_len": remlen, "xlp_sysid": sysid, "xlp_seg_size": segsize,
                          "xlp_xlog_blcksz": blcksz,
                          "controldata_sysid": controldata()["Database system identifier"]}
say(f"The first 40 bytes of `{fname}` (a long WAL page header):")
block(json.dumps(data["segment_header"], indent=2))

# =========================================================================== 5. vacuum
section("5. Vacuum, and the visibility map before and after")
vis_sql = f"""select blkno, all_visible, all_frozen, pd_all_visible
from pg_visibility('orders') where blkno in ({blk - 1}, {blk}, {blk + 1}, {nblk});
select * from pg_visibility_map_summary('orders');
select * from pg_freespace('orders') where blkno in ({blk}, {nblk});"""
psql(vis_sql, title="Before vacuum")
data["vm_before"] = {"summary": list(q("select * from pg_visibility_map_summary('orders')")[0]),
                     "pages": [list(r) for r in q(f"select blkno, all_visible, all_frozen from pg_visibility('orders') where not all_visible")]}
out = psql("vacuum (verbose) orders;", title="VACUUM (VERBOSE)", stderr=True)
data["vacuum1_verbose"] = out
psql(vis_sql + "\n" + items_sql("orders", blk, f"where lp = {lp}") + "\n" +
     items_sql("orders", nblk, f"where lp >= {nlp_}"), title="After vacuum")
data["vm_after1"] = {"summary": list(q("select * from pg_visibility_map_summary('orders')")[0]),
                     "pages": [list(r) for r in q("select blkno, all_visible, all_frozen from pg_visibility('orders') where not all_visible")]}
data["after_vacuum1"] = {"old": items_json("orders", blk, f"where lp = {lp}"),
                         "new": items_json("orders", nblk, f"where lp >= {nlp_}"),
                         "fsm": [list(r) for r in q(f"select blkno, avail from pg_freespace('orders') where blkno in ({blk}, {nblk})")]}
out = psql("vacuum (verbose, index_cleanup on) orders;",
           title="VACUUM (VERBOSE, INDEX_CLEANUP ON)",
           note="The first vacuum bypassed index cleanup; this forces it.", stderr=True)
data["vacuum2_verbose"] = out
psql(vis_sql + "\n" + items_sql("orders", blk, f"where lp = {lp}"), title="After the forced index cleanup")
data["vm_after2"] = {"summary": list(q("select * from pg_visibility_map_summary('orders')")[0]),
                     "pages": [list(r) for r in q("select blkno, all_visible, all_frozen from pg_visibility('orders') where not all_visible")]}
data["after_vacuum2"] = {"old": items_json("orders", blk, f"where lp = {lp}"),
                         "fsm": [list(r) for r in q(f"select blkno, avail from pg_freespace('orders') where blkno in ({blk}, {nblk})")]}

# the free space map itself
section("6. The free space map, page by page",
        "`pg_freespace` reports each heap page's free space in 32-byte steps; "
        "`fsm_page_contents` shows the tree stored inside each FSM page (non-zero nodes only).")
fsm_pages = q1("select pg_relation_size('orders', 'fsm') / 8192")
data["fsm_pages"] = fsm_pages
fsm_dump = {}
for b in range(fsm_pages):
    txt_ = q1(f"select fsm_page_contents(get_raw_page('orders', 'fsm', {b}))")
    fsm_dump[b] = txt_
    say(f"FSM block {b}:")
    block(txt_.strip() or "(all zero)")
data["fsm_page_contents"] = fsm_dump
ph_n = decode_page_header(raw_page("orders", nblk))
data["page_free_now"] = {"block": nblk, "pd_lower": ph_n["pd_lower"], "pd_upper": ph_n["pd_upper"],
                         "hole": ph_n["pd_upper"] - ph_n["pd_lower"],
                         "fsm_avail": q1(f"select avail from pg_freespace('orders') where blkno = {nblk}")}
block(json.dumps(data["page_free_now"], indent=2))

# =========================================================================== 7. TOAST
section("7. TOAST: where the size thresholds really are",
        "A scratch table with one int and one text column. Two kinds of value: text that "
        "compresses well, and md5 hex that pglz cannot shrink by the 25% it requires.")
psql("create table toast_probe (id int, v text);", record=False)
sizes = [500, 1000, 1500, 1900, 1960, 1990, 1999, 2000, 2001, 2010, 2100, 2500, 3000, 4000, 6000, 8000, 10000]
psql(f"""insert into toast_probe
select case k when 'c' then 0 else 100000 end + n,
       case k when 'c' then substr(repeat('refund pending; ', n / 16 + 1), 1, n)
              else substr((select string_agg(md5(g::text), '') from generate_series(1, n / 32 + 1) g), 1, n) end
from unnest(array['c','i']) k, unnest(array{sizes}) n;""",
     title="The probe: (int, text) rows, id = size, +100000 for the incompressible kind",
     note="Compressible text repeats a 16-byte phrase; incompressible text is md5 hex, which pglz "
          "cannot shrink by the 25% it requires.")


def varlena_fate(t_data):
    """The value starts 4 bytes into the row data (after the int). Its first byte says what it is."""
    h = t_data[4]
    if h == 0x01:
        return "out of line", 18
    if h & 0x01:
        return "inline, 1-byte header", h >> 1
    word = int.from_bytes(t_data[4:8], "little")
    size = word >> 2
    return ("compressed, inline" if word & 0x03 == 0x02 else "inline"), size


rows = q("""select ctid::text, id, octet_length(v), pg_column_size(v), pg_column_compression(v)::text
            from toast_probe order by id""")
sweep = []
for ctid_, ident, raw_n, stored, method in rows:
    b_, l_ = map(int, ctid_.strip("()").split(","))
    lp_len, t_data = q(f"select lp_len, t_data from heap_page_items(get_raw_page('toast_probe', {b_})) where lp = {l_}")[0]
    fate, in_row = varlena_fate(bytes(t_data))
    sweep.append({"kind": "incompressible" if ident >= 100000 else "compressible", "raw_bytes": raw_n,
                  "stored_bytes": stored, "method": method, "tuple_len": lp_len,
                  "bytes_in_row": in_row, "fate": fate})
data["toast_sweep"] = sweep
say("Each value, classified from the first byte of its varlena header in the heap tuple:")
block("\n".join(f"{r['kind']:15s} raw {r['raw_bytes']:>6,d}  stored {r['stored_bytes']:>6,d}  "
                 f"tuple {r['tuple_len']:>5,d}  in-row {r['bytes_in_row']:>5,d}  {r['method'] or '-':5s}  {r['fate']}"
                 for r in sweep))
t_toast = q1("select reltoastrelid::regclass::text from pg_class where relname = 'toast_probe'")
data["toast_chunks_by_value"] = [list(r) for r in q(f"""select chunk_id::bigint, count(*), sum(octet_length(chunk_data)),
    max(octet_length(chunk_data)) from {t_toast} group by 1 order by 3""")]
say(f"TOAST table {t_toast}: (chunk_id, chunks, bytes, largest chunk) = {data['toast_chunks_by_value']}")

# an UPDATE of another column leaves the TOASTed value alone
before_chunks = q(f"select chunk_id, count(*) from {t_toast} group by 1 order by 1")
l0 = q1("select pg_current_wal_insert_lsn()::text")
psql("update toast_probe set id = id + 1000000 where id = 110000;", record=False)
l1 = flush_lsn()
after_chunks = q(f"select chunk_id, count(*) from {t_toast} group by 1 order by 1")
data["toast_update_other_column"] = {"chunks_before": [list(r) for r in before_chunks],
                                     "chunks_after": [list(r) for r in after_chunks],
                                     "wal_bytes": lsn_int(l1) - lsn_int(l0)}
say(f"Updating the int column of the 10,000-byte incompressible row, whose text is out of line: TOAST chunks before "
    f"{before_chunks}, after {after_chunks}; WAL written {lsn_int(l1) - lsn_int(l0)} bytes.")

# the row of orders gets a wide note
section("8. Row 4242 gets a 10,000-byte note")
psql("alter table orders add column note text;",
     title="Adding a nullable column without a default",
     note="This changes only the catalog: no page of `orders` is rewritten.")
data["after_add_column"] = {"relfilenode": q1("select relfilenode from pg_class where relname = 'orders'"),
                            "pages": q1("select pg_relation_size('orders') / 8192"),
                            "natts_on_old_tuple": items_json("orders", blk, "where lp = 1")[0]["t_infomask2"] & 0x07FF}
say(f"relfilenode {data['after_add_column']['relfilenode']}, pages {data['after_add_column']['pages']}, "
    f"natts on an untouched tuple still {data['after_add_column']['natts_on_old_tuple']}.")
lsn6 = q1("select pg_current_wal_insert_lsn()::text")
psql(f"""update orders
set note = substr((select string_agg(md5(g::text), '') from generate_series(1, 313) g), 1, 10000)
where id = {ROW_ID};""", title="The update")
lsn7 = flush_lsn()
data["toast_update"] = {"lsn_before": lsn6, "lsn_after": lsn7,
                        "wal": wal_records(lsn6, lsn7, "The WAL the wide update wrote")}
psql(f"""select ctid, octet_length(note) as raw, pg_column_size(note) as stored,
       pg_column_compression(note) as method
from orders where id = {ROW_ID};""", title="The note as stored")
row_ctid3 = q1(f"select ctid::text from orders where id = {ROW_ID}")
b3, l3 = map(int, row_ctid3.strip("()").split(","))
data["toast_update"]["ctid"] = row_ctid3
psql(f"""select chunk_id, chunk_seq, octet_length(chunk_data) as bytes
from {data['toast_table']} order by chunk_id, chunk_seq;""", title=f"The chunks in {data['toast_table']}")
data["toast_update"]["chunks"] = [list(r) for r in q(
    f"select chunk_id::bigint, chunk_seq, octet_length(chunk_data) from {data['toast_table']} order by 1, 2")]
raw3 = raw_page("orders", b3)
lp3 = decode_line_pointer(raw3, l3)
tup3 = raw3[lp3["lp_off"]:lp3["lp_off"] + lp3["lp_len"]]
h3 = decode_tuple_header(tup3)
ptr = tup3[-18:]
va_rawsize, va_extinfo, va_valueid, va_toastrelid = struct.unpack_from("<iIII", ptr, 2)
data["toast_update"]["tuple"] = {"lp_len": lp3["lp_len"], "header": h3, "tuple_hex": tup3.hex()}
data["toast_update"]["pointer"] = {"hex": ptr.hex(), "va_header": f"{ptr[0]:02x}", "va_tag": ptr[1],
                                   "va_rawsize": va_rawsize, "va_extsize": va_extinfo & 0x3FFFFFFF,
                                   "compression_bits": va_extinfo >> 30, "va_valueid": va_valueid,
                                   "va_toastrelid": va_toastrelid, "toast_oid": toast_oid}
say(f"The row's tuple is now {lp3['lp_len']} bytes; its last 18 bytes are the TOAST pointer: `{ptr.hex(' ')}`")
block(json.dumps(data["toast_update"]["pointer"], indent=2))
psql(items_sql("orders", b3, f"where lp >= {nlp_}"), title=f"Page {b3}: the HOT chain now")
data["toast_update"]["page_items"] = items_json("orders", b3, f"where lp >= {nlp_}")

# =========================================================================== 9. the B-tree lookup
section("9. Finding the row through orders_customer_idx",
        "The row's customer is looked up the way an index scan would: metapage, root, one "
        "page per level, then the heap.")
cust = data["row_tuple_data"]["customer_id"]
data["btree_customer"] = cust
psql(f"""set enable_bitmapscan = off; set max_parallel_workers_per_gather = 0;
explain (analyze, buffers, costs off, timing off)
select id, status from orders where customer_id = {cust};""",
     title=f"The planner's view of `customer_id = {cust}`")
psql("select * from bt_metap('orders_customer_idx');", title="The metapage (block 0)")
meta = q("select root, level, fastroot, fastlevel from bt_metap('orders_customer_idx')")[0]
data["btree_meta"] = {"root": meta[0], "level": meta[1]}


def int_key(hexdata):
    if not hexdata:
        return None                    # minus infinity / truncated
    b = bytes.fromhex(hexdata.replace(" ", ""))
    return struct.unpack_from("<i", b, 0)[0]


walk = []
page = meta[0]
while True:
    st = q(f"""select blkno, type, live_items, free_size, btpo_prev, btpo_next, btpo_level
              from bt_page_stats('orders_customer_idx', {page})""")[0]
    its = q(f"""select itemoffset, ctid::text, itemlen, data, htid::text,
               (tids is not null) as posting, coalesce(array_length(tids, 1), 0), tids::text
               from bt_page_items('orders_customer_idx', {page}) order by itemoffset""")
    is_rightmost = st[5] == 0
    entry = {"block": st[0], "type": st[1], "live_items": st[2], "free_size": st[3],
             "prev": st[4], "next": st[5], "level": st[6]}
    first_data = 1 if is_rightmost else 2          # item 1 is the high key unless rightmost
    if not is_rightmost:
        entry["high_key"] = int_key(its[0][3])
    if st[6] > 0:
        chosen = None
        for it in its[first_data - 1:]:
            k = int_key(it[3])
            if k is None or k <= cust:
                chosen = it
        entry["downlink_key"] = int_key(chosen[3])
        entry["downlink_item"] = chosen[0]
        entry["next_block"] = int(chosen[1].strip("()").split(",")[0])
        nxt_items = [int_key(it[3]) for it in its[first_data - 1:]]
        entry["first_keys"] = nxt_items[:3]
        entry["last_key"] = nxt_items[-1]
        walk.append(entry)
        page = entry["next_block"]
        continue
    matches = [it for it in its if int_key(it[3]) == cust]
    entry["matches"] = [{"item": it[0], "ctid": it[1], "itemlen": it[2], "htid": it[4],
                         "posting": it[5], "ntids": it[6], "tids": it[7]} for it in matches]
    entry["first_key"] = int_key(its[first_data - 1][3])
    entry["last_key"] = int_key(its[-1][3])
    entry["posting_tuples_on_page"] = sum(1 for it in its if it[5])
    walk.append(entry)
    break
data["btree_walk"] = walk
for e in walk:
    say(f"Block {e['block']} (level {e['level']}, type {e['type']}): {e['live_items']} items, "
        f"{e['free_size']} bytes free" + (f", high key {e.get('high_key')}" if 'high_key' in e else "")
        + (f"; follows the downlink with key {e.get('downlink_key')} to block {e.get('next_block')}"
           if e['level'] > 0 else ""))
psql(f"""select itemoffset, ctid, itemlen, htid, tids
from bt_page_items('orders_customer_idx', {walk[-1]['block']})
where data = '{struct.pack('<i', cust).hex(' ')} 00 00 00 00';""",
     title=f"The leaf entries for customer {cust}")
psql(f"""select btpo_level as level, count(*) as pages, sum(live_items) as items,
       round(avg(free_size)) as avg_free_bytes
from bt_multi_page_stats('orders_customer_idx', 1, -1)
group by btpo_level order by btpo_level desc;""", title="The whole tree, by level")
data["btree_levels"] = [list(map(lambda x: float(x) if hasattr(x, "as_tuple") else x, r)) for r in q("""
    select btpo_level, count(*), sum(live_items), round(avg(free_size))
    from bt_multi_page_stats('orders_customer_idx', 1, -1) group by 1 order by 1 desc""")]
data["btree_posting"] = list(q("""select count(*) filter (where tids is not null),
       count(*), sum(coalesce(array_length(tids, 1), 1))
    from bt_multi_page_stats('orders_customer_idx', 1, -1) s,
         lateral bt_page_items('orders_customer_idx', s.blkno) i
    where s.btpo_level = 0 and (s.btpo_next = 0 or i.itemoffset > 1)""")[0])
say(f"Leaf level: {data['btree_posting'][0]} posting-list tuples out of {data['btree_posting'][1]} "
    f"leaf tuples, holding {data['btree_posting'][2]} heap TIDs.")
# the heap end of the walk
root_tid = [m for m in walk[-1]["matches"] if m["htid"] and m["htid"].startswith(f"({b3},")]
data["btree_heap_tid"] = root_tid[0]["htid"] if root_tid else None
psql(items_sql("orders", b3, f"where lp >= {nlp_}"),
     title=f"The heap end: the index says {data['btree_heap_tid']}, the chain says where the row is")

# =========================================================================== 10. a split
section("10. One B-tree page split, watched",
        "A fresh single-column index. 407 ascending integer keys fill its one leaf page; "
        "the 408th does not fit.")
psql("""create table split_demo (k int);
create index split_demo_k on split_demo (k);
insert into split_demo select generate_series(1, 407);""", record=False)
psql("""select root, level from bt_metap('split_demo_k');
select blkno, type, live_items, free_size, btpo_prev, btpo_next, btpo_level
from bt_page_stats('split_demo_k', 1);""", title="Before: one leaf page is the root")
data["split_before"] = {"meta": list(q("select root, level from bt_metap('split_demo_k')")[0]),
                        "leaf": list(q("select live_items, free_size from bt_page_stats('split_demo_k', 1)")[0])}
s0 = q1("select pg_current_wal_insert_lsn()::text")
psql("insert into split_demo values (408);", record=False)
s1 = flush_lsn()
psql("""select root, level from bt_metap('split_demo_k');
select blkno, type, live_items, free_size, btpo_prev, btpo_next, btpo_level
from bt_multi_page_stats('split_demo_k', 1, -1);
select itemoffset, ctid, itemlen, data from bt_page_items('split_demo_k', 3);
select itemoffset, ctid, data from bt_page_items('split_demo_k', 1) where itemoffset in (1, 2, 367);
select itemoffset, ctid, data from bt_page_items('split_demo_k', 2) where itemoffset in (1, 42);""",
     title="After the 408th key")
data["split_after"] = {"meta": list(q("select root, level from bt_metap('split_demo_k')")[0]),
                       "pages": [list(r) for r in q("""select blkno, type, live_items, free_size,
                           btpo_prev, btpo_next, btpo_level from bt_multi_page_stats('split_demo_k', 1, -1)""")],
                       "root_items": [[r[0], r[1], int_key(r[2])] for r in q(
                           "select itemoffset, ctid::text, data from bt_page_items('split_demo_k', 3)")],
                       "left_high_key": int_key(q1("select data from bt_page_items('split_demo_k', 1) where itemoffset = 1"))}
data["split_wal"] = wal_records(s0, s1, "The WAL the splitting insert wrote")

# a split in the middle of the tree: even keys first, then odd keys into the left leaf
psql("""create table split_mid (k int);
create index split_mid_k on split_mid (k);
insert into split_mid select g * 2 from generate_series(1, 408) g;""", record=False)
mid_before = [list(r) for r in q("""select blkno, live_items, free_size, btpo_next
    from bt_multi_page_stats('split_mid_k', 1, -1) where btpo_level = 0 order by blkno""")]
leaves0 = len(mid_before)
k, odd_inserted = 1, 0
while True:
    psql(f"insert into split_mid values ({k});", record=False)
    odd_inserted += 1
    if q1("select count(*) from bt_multi_page_stats('split_mid_k', 1, -1) where btpo_level = 0") > leaves0:
        break
    k += 2
psql("""select blkno, type, live_items, free_size, btpo_prev, btpo_next, btpo_level
from bt_multi_page_stats('split_mid_k', 1, -1) order by btpo_level desc, blkno;""",
     title="A split that is not at the right edge",
     note=f"408 even keys (one rightmost split already), then odd keys 1, 3, 5, ... into the left leaf "
          f"until it splits: that took {odd_inserted} inserts.")
data["split_mid"] = {"before": mid_before, "odd_inserted": odd_inserted,
                     "after": [list(r) for r in q("""select blkno, type, live_items, free_size, btpo_prev,
                         btpo_next, btpo_level from bt_multi_page_stats('split_mid_k', 1, -1)
                         order by btpo_level desc, blkno""")]}

# =========================================================================== 12. crash and replay
section("11. The last update, a crash, and the replay",
        "A checkpoint, one more update to row 4242, then `pg_ctl stop -m immediate`: the "
        "postmaster sends SIGQUIT to every process and nobody writes a dirty page.")
psql("checkpoint;", record=False)
cd_before = controldata(["Latest checkpoint location", "Latest checkpoint's REDO location",
                         "Latest checkpoint's REDO WAL file", "Database cluster state"])
data["crash"] = {"controldata_after_checkpoint": cd_before}
lsn8 = q1("select pg_current_wal_insert_lsn()::text")
out = psql(f"""begin;
update orders set amount_cents = 60000 where id = {ROW_ID};
select pg_current_xact_id() as xid;
commit;""", title="The update, committed",
           note="Nothing after this reads the table: a sequential scan here would drive the clock "
                "sweep, and the sweep may write the dirty page out before the crash (part 1).")
lsn9 = flush_lsn()
data["crash"]["xid"] = int(re.search(r"^\s*(\d+)\s*$", out, re.M).group(1))
cb = b3
cl = [it["lp"] for it in items_json("orders", cb, f"where lp >= {nlp_}") if it["t_xmin"] == str(data["crash"]["xid"])][0]
crash_ctid = f"({cb},{cl})"
data["crash"]["ctid"] = crash_ctid
psql(items_sql("orders", cb, f"where lp >= {nlp_}"), title=f"Page {cb} in shared buffers after the update")
psql(f"""select relblocknumber, isdirty, usagecount
from pg_buffercache
where reldatabase = (select oid from pg_database where datname = current_database())
  and relfilenode = pg_relation_filenode('orders') and relforknumber = 0 and relblocknumber = {cb};""",
     title="Is the page still dirty in shared buffers?")
data["crash"]["buffer_before_crash"] = list(q(f"""select isdirty, usagecount from pg_buffercache
    where reldatabase = (select oid from pg_database where datname = current_database())
      and relfilenode = pg_relation_filenode('orders') and relforknumber = 0 and relblocknumber = {cb}""")[0])
data["crash"]["wal"] = wal_records(lsn8, lsn9, "Its WAL: the first change to the page since the checkpoint")
crec = [r for r in data["crash"]["wal"] if r["rmgr"] == "Heap"][0]
data["crash"]["record_lsn"] = crec["start_lsn"]
data["crash"]["record_end_lsn"] = crec["end_lsn"]
data["crash"]["segment"] = q1(f"select file_name from pg_walfile_name_offset('{crec['start_lsn']}')")
mem = decode_page_header(raw_page("orders", cb))
disk = decode_page_header(disk_page("orders", cb))
data["crash"]["page_lsn_memory"] = mem["pd_lsn"]
data["crash"]["page_lsn_disk_before_crash"] = disk["pd_lsn"]
data["crash"]["disk_lower_before"] = disk["pd_lower"]
data["crash"]["mem_lower"] = mem["pd_lower"]
say(f"Page {cb}: pd_lsn in shared buffers {mem['pd_lsn']} (pd_lower {mem['pd_lower']}); "
    f"in the table file {disk['pd_lsn']} (pd_lower {disk['pd_lower']}).")

off = log_offset()
pg_ctl("-m", "immediate", "stop")
data["crash"]["controldata_while_down"] = controldata(["Database cluster state",
                                                       "Latest checkpoint's REDO location"])
disk_down = decode_page_header(open(PGDATA / data["relfilepath_orders"], "rb").read()[cb * BLCKSZ:(cb + 1) * BLCKSZ])
data["crash"]["page_lsn_disk_while_down"] = disk_down["pd_lsn"]
data["crash"]["disk_lower_while_down"] = disk_down["pd_lower"]
say(f"Server stopped with -m immediate. pg_controldata: {data['crash']['controldata_while_down']}. "
    f"Page {cb} in the file: pd_lsn {disk_down['pd_lsn']}, pd_lower {disk_down['pd_lower']}.")
t0 = time.time()
start_server()
data["crash"]["restart_seconds"] = round(time.time() - t0, 3)
rec_log = [l for l in log_since(off).splitlines() if l.strip()]
data["crash"]["server_log"] = rec_log
say("The server log from the stop to ready:")
block("\n".join(rec_log))
disk_after = decode_page_header(disk_page("orders", cb))
data["crash"]["page_lsn_disk_after_recovery"] = disk_after["pd_lsn"]
data["crash"]["disk_lower_after"] = disk_after["pd_lower"]
psql(f"select ctid, amount_cents from orders where id = {ROW_ID};", title="After recovery")
data["crash"]["amount_after"] = q1(f"select amount_cents from orders where id = {ROW_ID}")
data["crash"]["controldata_after"] = controldata(["Database cluster state", "Latest checkpoint location",
                                                  "Latest checkpoint's REDO location"])
say(f"Page {cb} in the table file after recovery: pd_lsn {disk_after['pd_lsn']}, pd_lower {disk_after['pd_lower']}.")

# =========================================================================== 13. archiving
section("12. Archiving: a second reader of the same segments",
        "Turned on with ALTER SYSTEM, which needs a restart; turned off the same way at the end.")
archive_dir = PGDATA.parent / "archive_demo"
shutil.rmtree(archive_dir, ignore_errors=True)
archive_dir.mkdir()
try:
    psql(f"""alter system set archive_mode = on;
alter system set archive_command = 'test ! -f {archive_dir}/%f && cp %p {archive_dir}/%f';""", record=False)
    restart_server()
    data["archive"] = {"processes": ps_children()}
    block(data["archive"]["processes"])
    sw = q1("select pg_walfile_name(pg_switch_wal())")
    for _ in range(40):
        time.sleep(0.25)
        if (archive_dir / sw).exists():
            break
    psql("""select archived_count, last_archived_wal, failed_count from pg_stat_archiver;""",
         title="pg_stat_archiver after one pg_switch_wal()")
    data["archive"]["switched_file"] = sw
    data["archive"]["archived"] = sorted(p.name for p in archive_dir.iterdir())
    data["archive"]["archive_status"] = sorted(p.name for p in (PGDATA / "pg_wal" / "archive_status").iterdir())
    data["archive"]["stat"] = list(q("select archived_count, last_archived_wal, failed_count from pg_stat_archiver")[0])
    say(f"Archive directory: {data['archive']['archived']}; pg_wal/archive_status: {data['archive']['archive_status']}")
finally:
    psql("alter system reset archive_mode; alter system reset archive_command;", record=False)
    restart_server()
    shutil.rmtree(archive_dir, ignore_errors=True)
data["archive"]["reset_ok"] = "archive" not in (PGDATA / "postgresql.auto.conf").read_text()

# =========================================================================== 14. a walsender
section("13. A walsender: the third reader",
        "`pg_receivewal` speaks the replication protocol, so the postmaster forks a walsender "
        "for it — the same process a streaming standby would get.")
with tempfile.TemporaryDirectory(dir=PGDATA.parent) as rdir:
    p = subprocess.Popen([str(PGBIN / "pg_receivewal"), "-D", rdir, "-h", str(SOCK), "-U", USER,
                          "--no-loop"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(1.5)
    psql("""select a.pid, a.backend_type, r.application_name, r.state, r.sent_lsn, r.write_lsn
from pg_stat_replication r join pg_stat_activity a using (pid);""",
         title="pg_stat_replication while pg_receivewal is attached")
    data["walsender"] = {"stat": [list(map(str, r)) for r in q(
        "select a.backend_type, r.application_name, r.state from pg_stat_replication r join pg_stat_activity a using (pid)")],
        "processes": ps_children()}
    try:
        sw2 = q1("select pg_walfile_name(pg_switch_wal())")
        time.sleep(1.5)
        data["walsender"]["received"] = sorted(os.listdir(rdir))
        data["walsender"]["switched_file"] = sw2
    finally:
        p.terminate()
        p.wait(timeout=10)
block(data["walsender"]["processes"])
say(f"Files pg_receivewal wrote: {data['walsender']['received']}")

# =========================================================================== 15. index-only scans
section("14. What the visibility map buys an index-only scan",
        "A scratch copy of `orders` with an index on `customer_id`. The plan is forced to an "
        "index-only scan so that only the visibility map changes between runs.")
psql("""create table ios_demo as select * from orders;
create index ios_demo_customer_idx on ios_demo (customer_id);
vacuum analyze ios_demo;""", record=False)
ios_sql = """set enable_seqscan = off; set enable_bitmapscan = off; set max_parallel_workers_per_gather = 0;
explain (analyze, buffers, costs off, timing off)
select count(*) from ios_demo where customer_id <= 10000;"""


def ios_run(title, note=None):
    out = psql(ios_sql, title=title, note=note)
    return {"heap_fetches": int(re.search(r"Heap Fetches: (\d+)", out).group(1)),
            "shared_hit": int(re.search(r"shared hit=(\d+)", out).group(1)),
            "shared_read": int(m.group(1)) if (m := re.search(r"read=(\d+)", out)) else 0,
            "plan": out}


data["ios"] = {"clean": ios_run("All pages all-visible")}
psql("update ios_demo set amount_cents = amount_cents + 1 where id % 50 = 0;",
     title="Touch one row in fifty", note="20,000 rows, spread over every page of the table.")
data["ios"]["vm_after_update"] = list(q("select * from pg_visibility_map_summary('ios_demo')")[0])
data["ios"]["dirty"] = ios_run("After the update, before vacuum")
psql("vacuum ios_demo;", record=False)
data["ios"]["vm_after_vacuum"] = list(q("select * from pg_visibility_map_summary('ios_demo')")[0])
data["ios"]["vacuumed"] = ios_run("After vacuum")
data["ios"]["pages"] = q1("select pg_relation_size('ios_demo') / 8192")

# =========================================================================== done
data["checkpoints_total"] = checkpoints_so_far()
data["auto_conf_clean"] = (PGDATA / "postgresql.auto.conf").read_text().count("=") == 0
CAP_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
CAP_JSON.write_text(json.dumps(data, indent=2, default=str) + "\n", encoding="utf-8")
print(f"wrote {CAP_MD.name} and {CAP_JSON.name}")
