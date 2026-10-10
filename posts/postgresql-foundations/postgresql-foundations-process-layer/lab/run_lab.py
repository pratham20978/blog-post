#!/usr/bin/env python3
"""Reproducible lab for "How PostgreSQL Uses Processes" (postgresql-foundations, part 2).

Every number quoted in blog.md that came from a running server came from this script.
It drives a stock PostgreSQL 16.2 (the `pgserver` wheel's bundled binaries) with the
default postgresql.conf, on a data directory that lives on a real disk (not tmpfs), and
writes two files next to itself:

    captures.md    the psql output of every step, verbatim, in run order
    captures.json  the numbers the figures are drawn from

The two tables are byte-for-byte the ones part 1 used (`customers`, 710 pages;
`orders`, 7,693 pages) so the series' numbers line up. Part 2 adds two indexes on
`orders` and a scratch copy of it, because vacuum's interesting behaviour is in the
index passes.

Where a step changes a setting away from the default it says so in the capture, and
sets it back. Two steps deliberately break things: step 15 kills a backend with
SIGKILL to watch the postmaster's crash handling, and step 9 holds a snapshot open to
block vacuum. Run this against a throwaway cluster, never a real one.

Prerequisites (see README.md): PGBIN pointing at a 16.x bin directory, `psycopg` 3,
and a data directory on a non-tmpfs filesystem.

Run:  PGBIN=/path/to/bin PGDATA=/path/to/pgdata PGSOCK=/path/to/sock python3 run_lab.py
"""
import json
import os
import pathlib
import re
import signal
import subprocess
import sys
import time

import psycopg

HERE = pathlib.Path(__file__).resolve().parent
PGBIN = pathlib.Path(os.environ["PGBIN"])
PGDATA = pathlib.Path(os.environ["PGDATA"]).resolve()
SOCK = pathlib.Path(os.environ.get("PGSOCK", PGDATA.parent / "sock")).resolve()
DB = "proclab"
USER = "postgres"

CAP_MD = HERE / "captures.md"
CAP_JSON = HERE / "captures.json"
md = []
data = {}


# --------------------------------------------------------------------------- plumbing
def pg_ctl(*args):
    return subprocess.run([str(PGBIN / "pg_ctl"), "-D", str(PGDATA), *args],
                          check=True, capture_output=True, text=True)


def start_server():
    pg_ctl("-w", "-o", '-h ""', "-o", f"-k {SOCK}", "-l", str(PGDATA / "server.log"), "start")
    time.sleep(0.5)


def restart_server():
    """Stop and start the postmaster. Every child process is replaced."""
    pg_ctl("-w", "stop")
    start_server()


def dsn(db=DB):
    return f"host={SOCK} user={USER} dbname={db}"


def psql(sql, db=DB, title=None, note=None, record=True, tolerate=False):
    """Run SQL through psql and keep its text output, exactly as a reader would see it."""
    out = subprocess.run([str(PGBIN / "psql"), "-X", "-q", "-h", str(SOCK), "-U", USER, "-d", db,
                          "-v", "ON_ERROR_STOP=1"],
                         input=sql, capture_output=True, text=True)
    if out.returncode != 0 and not tolerate:
        raise RuntimeError(f"psql failed:\n{sql}\n{out.stderr}")
    text = (out.stdout + out.stderr).rstrip("\n") if tolerate else out.stdout.rstrip("\n")
    if record:
        md.append(f"### {title}\n" if title else "")
        if note:
            md.append(note + "\n")
        md.append("```sql\n" + sql.strip() + "\n```\n")
        md.append("```text\n" + text + "\n```\n")
    return text


def q(sql, db=DB):
    """Scalar / row fetch through psycopg for the JSON side."""
    with psycopg.connect(dsn(db), autocommit=True) as c:
        return c.execute(sql).fetchall()


def rel_path(rel):
    return PGDATA / q(f"select pg_relation_filepath('{rel}')")[0][0]


def drop_from_kernel_cache(path):
    """posix_fadvise(DONTNEED) needs no privilege on a file we own."""
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
        os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
    finally:
        os.close(fd)


def rss_kb(pid):
    try:
        for line in open(f"/proc/{pid}/status"):
            if line.startswith("VmRSS:"):
                return int(line.split()[1])
    except FileNotFoundError:
        return None
    return None


def postmaster_pid():
    return int((PGDATA / "postmaster.pid").read_text().splitlines()[0])


def ps_tree(ppid):
    """The postmaster and its children, straight from ps."""
    out = subprocess.run(
        ["ps", "-o", "pid=,ppid=,rss=,args=", "--ppid", str(ppid), "-p", str(ppid)],
        capture_output=True, text=True).stdout
    return "\n".join(l.rstrip() for l in out.splitlines() if l.strip())


def section(title, blurb=None):
    md.append(f"\n## {title}\n")
    if blurb:
        md.append(blurb + "\n")


def block(text, lang="text"):
    md.append(f"```{lang}\n{text}\n```\n")


def logtail(n=40, since_offset=0):
    t = (PGDATA / "server.log").read_text(errors="replace")
    return "\n".join(t[since_offset:].splitlines()[-n:])


def log_offset():
    return (PGDATA / "server.log").stat().st_size


def num(text, pattern, cast=int):
    m = re.search(pattern, text)
    return cast(m.group(1)) if m else None


# --------------------------------------------------------------------------- 0. fresh database
md.append("# Lab captures — How PostgreSQL Uses Processes\n")
md.append("Generated by `run_lab.py`. PostgreSQL 16.2, default `postgresql.conf` except where a "
          "step says otherwise.\n")

if not (PGDATA / "postmaster.pid").exists():
    start_server()

psql(f"drop database if exists {DB};", db="postgres", record=False)
psql(f"create database {DB};", db="postgres", record=False)
psql("create extension pg_buffercache; create extension pg_prewarm;", record=False)
psql("select pg_stat_reset_shared('io'), pg_stat_reset_shared('wal'), "
     "pg_stat_reset_shared('bgwriter');", record=False)

machine = {
    "cpu": subprocess.run(["nproc"], capture_output=True, text=True).stdout.strip(),
    "mem_mb": int(re.search(r"MemTotal:\s+(\d+)", open("/proc/meminfo").read()).group(1)) // 1024,
    "disk": "Samsung NVMe (MZVL8512HELU), ext4",
    "kernel": os.uname().release,
}
data["machine"] = machine
data["version"] = q("select version()")[0][0]
md.append(f"Machine: {machine['cpu']} CPUs, {machine['mem_mb']} MB RAM, {machine['disk']}, "
          f"Linux {machine['kernel']}.\n")
md.append(f"Server: `{data['version']}`\n")

# --------------------------------------------------------------------------- 1. who is running
section("1. Every process this server is running, and who forked it",
        "Straight after start, with no client connected. `ps --ppid <postmaster>` shows the "
        "parent of every one of them is the postmaster.")
pm = postmaster_pid()
data["postmaster_pid"] = pm
tree = ps_tree(pm)
block(tree)
data["ps_tree_idle"] = tree

psql("""select pid, backend_type, backend_start::time(0) as started,
       case when backend_type = 'client backend' then client_addr::text else null end as client
from pg_stat_activity
order by backend_start;""", title="pg_stat_activity, one row per process",
     note="Auxiliary processes have appeared in `pg_stat_activity` since PostgreSQL 10, when the "
          "`backend_type` column was added; the archiver joined the list in 14.")
data["backend_types_idle"] = [list(r) for r in
                              q("select backend_type, count(*) from pg_stat_activity group by 1 order by 1")]

psql("""select name, setting, boot_val, context
from pg_settings
where name in ('max_connections','max_worker_processes','max_parallel_workers',
               'max_parallel_workers_per_gather','max_parallel_maintenance_workers',
               'autovacuum','autovacuum_max_workers','autovacuum_naptime',
               'bgwriter_delay','bgwriter_lru_maxpages','bgwriter_lru_multiplier',
               'checkpoint_timeout','checkpoint_completion_target','max_wal_size',
               'wal_writer_delay','wal_writer_flush_after','synchronous_commit',
               'commit_delay','commit_siblings','log_checkpoints','log_autovacuum_min_duration',
               'autovacuum_vacuum_threshold','autovacuum_vacuum_scale_factor',
               'autovacuum_vacuum_insert_threshold','autovacuum_vacuum_insert_scale_factor',
               'autovacuum_analyze_threshold','autovacuum_analyze_scale_factor',
               'autovacuum_vacuum_cost_delay','autovacuum_vacuum_cost_limit',
               'vacuum_cost_page_hit','vacuum_cost_page_miss','vacuum_cost_page_dirty',
               'vacuum_cost_limit','autovacuum_freeze_max_age','vacuum_freeze_min_age',
               'vacuum_freeze_table_age','vacuum_failsafe_age','maintenance_work_mem',
               'max_wal_senders','max_logical_replication_workers','restart_after_crash')
order by name;""", title="The process-layer defaults this lab runs with")
data["settings"] = {r[0]: {"setting": r[1], "boot_val": r[2], "context": r[3]} for r in
                    q("select name, setting, boot_val, context from pg_settings")}

# --------------------------------------------------------------------------- 2. fork cost
section("2. What a connection costs",
        "Each new connection is a `fork()` from the postmaster plus authentication plus "
        "`InitPostgres`. The comparison is 200 fresh connections against 200 round trips "
        "on one already-open connection.")

t0 = time.perf_counter()
for _ in range(200):
    c = psycopg.connect(dsn())
    c.execute("select 1")
    c.close()
t_fresh = time.perf_counter() - t0

with psycopg.connect(dsn(), autocommit=True) as c:
    c.execute("select 1")
    t0 = time.perf_counter()
    for _ in range(200):
        c.execute("select 1")
    t_reuse = time.perf_counter() - t0

data["conn_cost"] = {
    "fresh_200_s": round(t_fresh, 4),
    "fresh_each_ms": round(t_fresh / 200 * 1000, 3),
    "reuse_200_s": round(t_reuse, 4),
    "reuse_each_ms": round(t_reuse / 200 * 1000, 4),
    "ratio": round((t_fresh / 200) / (t_reuse / 200), 1),
}
block(json.dumps(data["conn_cost"], indent=2))

# a backend's resident memory, fresh versus after it has touched the catalogs
with psycopg.connect(dsn(), autocommit=True) as c:
    bpid = c.execute("select pg_backend_pid()").fetchone()[0]
    rss_fresh = rss_kb(bpid)
    c.execute("select count(*) from pg_class")
    rss_cat = rss_kb(bpid)
    for t in ("customers",):
        pass
    c.execute("select 1")
    rss_end = rss_kb(bpid)
data["backend_rss_kb"] = {"fresh": rss_fresh, "after_catalog_scan": rss_cat, "end": rss_end}
block(json.dumps(data["backend_rss_kb"], indent=2))

# --------------------------------------------------------------------------- 3. the tables
section("3. The same two tables part 1 used, plus indexes for the vacuum work")
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
vacuum analyze orders;""", title="Schema and load")

psql("""select relname,
       pg_relation_size(oid) / 8192 as pages,
       pg_size_pretty(pg_relation_size(oid)) as size,
       reltuples::bigint as rows
from pg_class
where relname in ('customers','customers_pkey','orders','orders_customer_idx','orders_created_idx')
order by pg_relation_size(oid) desc;""", title="Sizes in pages")
data["pages"] = {r[0]: r[1] for r in q("""select relname, pg_relation_size(oid) / 8192 from pg_class
    where relname in ('customers','customers_pkey','orders','orders_customer_idx','orders_created_idx')""")}

# --------------------------------------------------------------------------- 4. the checkpointer
section("4. A checkpoint, timed",
        "`log_checkpoints` is on by default since PostgreSQL 15, so the server log records every "
        "checkpoint's page count and its three phases. Dirty a large number of buffers, then ask "
        "for a checkpoint and read the log line back.")

before = q("""select checkpoints_timed, checkpoints_req, checkpoint_write_time, checkpoint_sync_time,
       buffers_checkpoint, buffers_clean, maxwritten_clean, buffers_backend,
       buffers_backend_fsync, buffers_alloc from pg_stat_bgwriter""")[0]
off = log_offset()
psql("update customers set name = name || '.' where id % 2 = 0;", record=False)
dirty = q("select count(*) from pg_buffercache where isdirty")[0][0]
t0 = time.perf_counter()
psql("checkpoint;", record=False)
t_ckpt = time.perf_counter() - t0
after = q("""select checkpoints_timed, checkpoints_req, checkpoint_write_time, checkpoint_sync_time,
       buffers_checkpoint, buffers_clean, maxwritten_clean, buffers_backend,
       buffers_backend_fsync, buffers_alloc from pg_stat_bgwriter""")[0]
cols = ["checkpoints_timed", "checkpoints_req", "checkpoint_write_time", "checkpoint_sync_time",
        "buffers_checkpoint", "buffers_clean", "maxwritten_clean", "buffers_backend",
        "buffers_backend_fsync", "buffers_alloc"]
data["checkpoint"] = {
    "dirty_buffers_before": dirty,
    "manual_checkpoint_seconds": round(t_ckpt, 4),
    "before": dict(zip(cols, before)),
    "after": dict(zip(cols, after)),
    "delta": {c: (b - a) for c, a, b in zip(cols, before, after)},
}
md.append(f"{dirty} of the 16,384 buffers were dirty when the checkpoint was requested. "
          f"`CHECKPOINT` returned in {t_ckpt * 1000:.0f} ms.\n")
block(json.dumps(data["checkpoint"], indent=2, default=str))
ck_log = [l for l in (PGDATA / "server.log").read_text(errors="replace")[off:].splitlines()
          if "checkpoint" in l.lower()]
data["checkpoint_log"] = ck_log
block("\n".join(ck_log))

# leave customers clean, so step 7b's threshold experiment starts from zero dead tuples
psql("vacuum analyze customers;", record=False)
psql("""select checkpoints_timed, checkpoints_req, buffers_checkpoint, buffers_clean,
       buffers_backend, maxwritten_clean
from pg_stat_bgwriter;""",
     title="pg_stat_bgwriter after the checkpoint",
     note="On PostgreSQL 17 the five checkpoint columns move to `pg_stat_checkpointer` and are "
          "renamed; on 16 they are still here.")

# --------------------------------------------------------------------------- 5. who writes pages
section("5. Which process actually wrote each dirty page",
        "`pg_stat_io` (PostgreSQL 16 and later) splits every read and write by the process type "
        "that did it. This is the only view that separates the checkpointer, the background "
        "writer and the backends.")
psql("""select backend_type, context, writes, fsyncs, extends, evictions, reuses
from pg_stat_io
where object = 'relation' and (writes > 0 or evictions > 0 or reuses > 0 or extends > 0)
order by writes desc nulls last;""", title="pg_stat_io by backend type")
data["stat_io"] = [list(r) for r in q("""select backend_type, context, writes, fsyncs, extends,
    evictions, reuses from pg_stat_io where object = 'relation'
    and (writes > 0 or evictions > 0 or reuses > 0 or extends > 0)""")]

# --------------------------------------------------------------------------- 6. the WAL writer
section("6. synchronous_commit, measured",
        "5,000 single-row transactions, first with the default `synchronous_commit = on` (every "
        "commit waits for its WAL to be flushed), then with `off` (the WAL writer flushes it "
        "within three `wal_writer_delay` intervals instead).")

psql("create table commits (id serial primary key, v int);", record=False)


def commit_loop(sync, n=5000):
    with psycopg.connect(dsn()) as c:
        c.execute(f"set synchronous_commit = {sync}")
        c.commit()
        cur = c.cursor()
        t0 = time.perf_counter()
        for i in range(n):
            cur.execute("insert into commits (v) values (%s)", (i,))
            c.commit()
        return time.perf_counter() - t0


wal_before = q("select wal_records, wal_bytes, wal_write, wal_sync, wal_write_time, wal_sync_time "
               "from pg_stat_wal")[0]
t_on = commit_loop("on")
wal_mid = q("select wal_records, wal_bytes, wal_write, wal_sync, wal_write_time, wal_sync_time "
            "from pg_stat_wal")[0]
t_off = commit_loop("off")
wal_after = q("select wal_records, wal_bytes, wal_write, wal_sync, wal_write_time, wal_sync_time "
              "from pg_stat_wal")[0]
wcols = ["wal_records", "wal_bytes", "wal_write", "wal_sync", "wal_write_time", "wal_sync_time"]
data["sync_commit"] = {
    "n": 5000,
    "on_seconds": round(t_on, 4), "on_tps": round(5000 / t_on, 1),
    "off_seconds": round(t_off, 4), "off_tps": round(5000 / t_off, 1),
    "speedup": round(t_on / t_off, 2),
    "wal_on": dict(zip(wcols, [b - a for a, b in zip(wal_before, wal_mid)])),
    "wal_off": dict(zip(wcols, [b - a for a, b in zip(wal_mid, wal_after)])),
}
block(json.dumps(data["sync_commit"], indent=2, default=str))
psql("select wal_records, wal_fpi, wal_bytes, wal_buffers_full, wal_write, wal_sync from pg_stat_wal;",
     title="pg_stat_wal for the whole run")

# --------------------------------------------------------------------------- 7. autovacuum's arithmetic
section("7. When autovacuum decides a table needs vacuuming",
        "The threshold is `autovacuum_vacuum_threshold + autovacuum_vacuum_scale_factor * reltuples`, "
        "compared against the statistics collector's estimate of dead tuples. Nothing here is "
        "hypothetical: the numbers are read out of `pg_settings` and `pg_class` and the comparison "
        "is done in SQL.")
psql("""select c.relname,
       c.reltuples::bigint as reltuples,
       current_setting('autovacuum_vacuum_threshold')::int as base,
       current_setting('autovacuum_vacuum_scale_factor')::float as scale,
       (current_setting('autovacuum_vacuum_threshold')::int
        + current_setting('autovacuum_vacuum_scale_factor')::float * c.reltuples)::bigint
         as vacuum_threshold,
       (current_setting('autovacuum_vacuum_insert_threshold')::int
        + current_setting('autovacuum_vacuum_insert_scale_factor')::float * c.reltuples)::bigint
         as insert_threshold,
       (current_setting('autovacuum_analyze_threshold')::int
        + current_setting('autovacuum_analyze_scale_factor')::float * c.reltuples)::bigint
         as analyze_threshold,
       s.n_dead_tup, s.n_ins_since_vacuum, s.n_mod_since_analyze
from pg_class c join pg_stat_all_tables s on s.relid = c.oid
where c.relname in ('customers','orders');""", title="The three thresholds, computed")
data["thresholds"] = [list(r) for r in q("""select c.relname, c.reltuples::bigint,
    (50 + 0.2 * c.reltuples)::bigint, (1000 + 0.2 * c.reltuples)::bigint,
    (50 + 0.1 * c.reltuples)::bigint, s.n_dead_tup
    from pg_class c join pg_stat_all_tables s on s.relid = c.oid
    where c.relname in ('customers','orders')""")]

# now actually cross the threshold on `customers` and wait for the launcher
section("7b. Crossing the threshold and watching a worker appear",
        "`customers` has 100,000 rows, so its vacuum threshold is 20,050 dead tuples. Update "
        "30,000 rows and wait. `autovacuum_naptime` is the default 60 seconds and the launcher "
        "divides its naptime by the number of databases, so the wait is under a minute; nothing "
        "was tuned to make this happen.")
# log_autovacuum_min_duration defaults to -1 (log nothing). Set it to 0 for this step so
# the worker's own report lands in the server log, and put it back afterwards.
psql("alter system set log_autovacuum_min_duration = 0;", db="postgres", record=False)
psql("select pg_reload_conf();", db="postgres", record=False)
av_off = log_offset()
psql("select pg_stat_reset();", record=False)
psql("update customers set name = name || 'x' where id <= 30000;", record=False)
watch = psycopg.connect(dsn(), autocommit=True)         # one connection, not 600
wcur = watch.cursor()
t0 = time.perf_counter()
seen_worker = None
appeared = None
for _ in range(14000):                                  # up to ~140 s at 10 ms
    rows = wcur.execute("""select pid, backend_type, query from pg_stat_activity
                           where backend_type = 'autovacuum worker'""").fetchall()
    if rows and seen_worker is None:
        seen_worker = [list(r) for r in rows]
    r = wcur.execute("""select n_dead_tup, autovacuum_count, last_autovacuum
                        from pg_stat_all_tables where relname = 'customers'""").fetchone()
    if r and r[1] and r[1] > 0:
        appeared = round(time.perf_counter() - t0, 1)
        break
    time.sleep(0.01)
watch.close()
data["autovacuum_trigger"] = {
    "seconds_until_autovacuum": appeared,
    "worker_seen_in_pg_stat_activity": seen_worker,
}
block(json.dumps(data["autovacuum_trigger"], indent=2, default=str))
psql("""select relname, n_live_tup, n_dead_tup, n_mod_since_analyze,
       autovacuum_count, analyze_count, last_autovacuum, last_autoanalyze
from pg_stat_all_tables where relname in ('customers','orders');""",
     title="pg_stat_all_tables after the launcher got there")
av_text = (PGDATA / "server.log").read_text(errors="replace")[av_off:]
autolog, keep = [], False
for l in av_text.splitlines():                          # the log entry is multi-line
    if "automatic vacuum" in l or "automatic analyze" in l:
        keep = True
    elif l and not l.startswith(("\t", " ")) and "LOG:" in l:
        keep = False
    if keep:
        autolog.append(l)
data["autovacuum_log"] = autolog[:40]
block("\n".join(autolog[:40]) or "(no autovacuum log entry captured)")
psql("alter system reset log_autovacuum_min_duration;", db="postgres", record=False)
psql("select pg_reload_conf();", db="postgres", record=False)

# --------------------------------------------------------------------------- 8. index passes
section("8. The number that decides how long a vacuum takes",
        "`maintenance_work_mem` holds the list of dead tuple identifiers. When the list fills, "
        "vacuum must stop, scan **every index in full**, empty the list and resume the heap scan "
        "where it left off. So the memory setting does not make vacuum a little faster: it "
        "multiplies the number of complete index scans. Same table, same deletion, two settings.")

psql("""create table vac_demo as select * from orders;
create index vac_demo_customer_idx on vac_demo (customer_id);
create index vac_demo_created_idx  on vac_demo (created);
vacuum analyze vac_demo;""", record=False)


def vacuum_run(mwm, cold=False):
    """Rebuild the scratch table, delete 80% of it, vacuum with the given memory budget.

    With cold=True the server is restarted (shared buffers are emptied) and the heap and
    both index files are evicted from the kernel page cache first, so every index pass is
    a real read from disk. That is the case the index-pass multiplier actually bites in."""
    psql("truncate vac_demo;", record=False)
    psql("""insert into vac_demo select * from orders;
            vacuum analyze vac_demo;""", record=False)
    psql("delete from vac_demo where id % 5 <> 0;", record=False)   # 800,000 dead tuples
    dead = q("select n_dead_tup from pg_stat_all_tables where relname = 'vac_demo'")[0][0]
    if cold:
        paths = [rel_path(r) for r in
                 ("vac_demo", "vac_demo_customer_idx", "vac_demo_created_idx")]
        psql("checkpoint;", record=False)
        restart_server()
        for pth in paths:
            drop_from_kernel_cache(pth)
    t0 = time.perf_counter()
    out = psql(f"set maintenance_work_mem = '{mwm}'; vacuum (verbose) vac_demo;",
               title=f"VACUUM VERBOSE with maintenance_work_mem = {mwm}"
                     + (" (cold cache)" if cold else " (warm cache)"),
               note=f"{dead:,} dead tuples to remove, two indexes"
                    + (", shared buffers and kernel cache both emptied first." if cold
                       else ", everything already in shared buffers."),
               tolerate=True)
    took = time.perf_counter() - t0
    scans = num(out, r"index scans:\s*(\d+)")
    return {"maintenance_work_mem": mwm, "dead_tuples": dead, "cold": cold,
            "index_scans": scans, "seconds": round(took, 3),
            "buffer_hits": num(out, r"buffer usage:\s*(\d+) hits"),
            "buffer_misses": num(out, r"buffer usage:\s*\d+ hits,\s*(\d+) misses"),
            "wal_records": num(out, r"WAL usage:\s*(\d+) records"),
            "verbose": out}


small = vacuum_run("1MB")
big = vacuum_run("256MB")
small_cold = vacuum_run("1MB", cold=True)
big_cold = vacuum_run("256MB", cold=True)
data["vacuum_index_passes"] = {
    "small": small, "big": big, "small_cold": small_cold, "big_cold": big_cold,
    "warm_ratio": round(small["seconds"] / big["seconds"], 2) if big["seconds"] else None,
    "cold_ratio": round(small_cold["seconds"] / big_cold["seconds"], 2) if big_cold["seconds"] else None,
}
md.append(
    f"Warm: 1 MB made **{small['index_scans']}** complete passes over both indexes in "
    f"{small['seconds']:.2f} s; 256 MB made **{big['index_scans']}** in {big['seconds']:.2f} s. "
    f"The pass count multiplies but the clock barely moves, because the indexes are already in "
    f"memory.\n\nCold (server restarted, both index files evicted from the kernel cache): 1 MB "
    f"made **{small_cold['index_scans']}** passes in {small_cold['seconds']:.2f} s against "
    f"**{big_cold['index_scans']}** pass in {big_cold['seconds']:.2f} s — "
    f"{data['vacuum_index_passes']['cold_ratio']}x. That is the same multiplier, paid at disk "
    f"latency instead of memory latency.\n")
block(json.dumps({k: v for k, v in data["vacuum_index_passes"].items() if k != "verbose"},
                 indent=2, default=str))

# how many TIDs fit in a given maintenance_work_mem on 16.x
data["tid_math"] = {
    "bytes_per_tid_pg16": 6,
    "tids_in_1mb": (1 << 20) // 6,
    "tids_in_64mb": (64 << 20) // 6,
    "tids_in_256mb": (256 << 20) // 6,
    "hard_cap_pg16": 178_956_970,
}
block(json.dumps(data["tid_math"], indent=2))

# --------------------------------------------------------------------------- 9. a held snapshot
section("9. One idle transaction, and nothing can be cleaned",
        "A second session opens a REPEATABLE READ transaction and does nothing else. Its snapshot "
        "pins the oldest transaction id the whole cluster may remove behind. Vacuum runs, walks "
        "every page, and removes nothing.")
psql("truncate vac_demo;", record=False)
psql("insert into vac_demo select * from orders; vacuum analyze vac_demo;", record=False)

holder = psycopg.connect(dsn())
hc = holder.cursor()
hc.execute("begin isolation level repeatable read")
hc.execute("select count(*) from vac_demo")
holder_pid = hc.execute("select pg_backend_pid()").fetchone()[0]
hx = q("""select pid, state, backend_xmin, xact_start::time(0),
          now() - xact_start as open_for
          from pg_stat_activity where pid = %s""" % holder_pid)
data["holder"] = [list(r) for r in hx]
psql("delete from vac_demo where id % 5 <> 0;", record=False)
blocked = psql("set maintenance_work_mem = '256MB'; vacuum (verbose) vac_demo;",
               title="VACUUM while the snapshot is held", tolerate=True)
# PostgreSQL 16 words this as "N removed, M remain, K are dead but not yet removable"
# with a "removable cutoff: X" line, rather than the older "oldest xmin" wording.
data["vacuum_blocked"] = {
    "removed": num(blocked, r"tuples:\s*(\d+) removed"),
    "nonremovable": num(blocked, r"(\d+) are dead but not yet removable"),
    "removable_cutoff": num(blocked, r"removable cutoff:\s*(\d+)"),
    "cutoff_age": num(blocked, r"removable cutoff:\s*\d+, which was (\d+) XIDs old"),
    "index_scans": num(blocked, r"index scans:\s*(\d+)"),
    "pages_scanned": num(blocked, r"(\d+) scanned \("),
    "verbose": blocked,
}
psql("""select pid, backend_type, state, backend_xmin,
       date_trunc('second', now() - xact_start) as transaction_open_for
from pg_stat_activity where backend_xmin is not null order by age(backend_xmin) desc;""",
     title="Who is holding the horizon back")
hc.execute("commit")
holder.close()
time.sleep(0.3)
after_release = psql("set maintenance_work_mem = '256MB'; vacuum (verbose) vac_demo;",
                     title="The same VACUUM once that session commits",
                     tolerate=True)
data["vacuum_released"] = {
    "removed": num(after_release, r"tuples:\s*(\d+) removed"),
    "nonremovable": num(after_release, r"(\d+) are dead but not yet removable"),
    "removable_cutoff": num(after_release, r"removable cutoff:\s*(\d+)"),
    "index_scans": num(after_release, r"index scans:\s*(\d+)"),
    "verbose": after_release,
}
block(json.dumps({"blocked": {k: v for k, v in data["vacuum_blocked"].items() if k != "verbose"},
                  "released": {k: v for k, v in data["vacuum_released"].items() if k != "verbose"}},
                 indent=2, default=str))

# --------------------------------------------------------------------------- 10. vacuum progress
section("10. Watching a vacuum move through its phases",
        "`pg_stat_progress_vacuum` is sampled from another session while a vacuum of the 60 MB "
        "table runs. The phase names are vacuum's own state machine.")
psql("truncate vac_demo;", record=False)
psql("insert into vac_demo select * from orders; vacuum analyze vac_demo;", record=False)
psql("delete from vac_demo where id % 5 <> 0;", record=False)

runner = psycopg.connect(dsn(), autocommit=True)
rc = runner.cursor()
rc.execute("set maintenance_work_mem = '1MB'")   # force several index passes
import threading
obs = psycopg.connect(dsn(), autocommit=True)          # one observer, reused by every sampler
ocur = obs.cursor()


def sample(sql):
    return ocur.execute(sql).fetchall()


def in_thread(fn):
    """Run fn in a thread and keep whatever it raises instead of printing a traceback."""
    box = {}

    def wrapper():
        try:
            box["value"] = fn()
        except Exception as e:                           # noqa: BLE001
            box["error"] = str(e).strip().splitlines()[0]
    t = threading.Thread(target=wrapper)
    t.start()
    return t, box


phases = []


def do_vacuum():
    rc.execute("vacuum vac_demo")


th, _ = in_thread(do_vacuum)
raw = []
while th.is_alive():
    rows = sample("""select phase, heap_blks_total, heap_blks_scanned, heap_blks_vacuumed,
                index_vacuum_count, max_dead_tuples, num_dead_tuples
                from pg_stat_progress_vacuum""")
    for r in rows:
        rec = list(r)
        if not raw or raw[-1] != rec:
            raw.append(rec)
th.join()
runner.close()
# keep every phase transition (the row before and after), plus a thin regular sample of
# the long scanning stretches, so the stored trace spans the whole run
keep = []
for i, rec in enumerate(raw):
    transition = i == 0 or rec[0] != raw[i - 1][0] or (i + 1 < len(raw) and raw[i + 1][0] != rec[0])
    if transition or i % 25 == 0:
        keep.append(rec)
phases = keep
data["vacuum_progress"] = phases
data["vacuum_progress_samples"] = len(raw)
block(f"{len(raw)} distinct samples; phase transitions and every 25th sample shown\n"
      "phase | heap_total | heap_scanned | heap_vacuumed | index_vac_count | max_dead | num_dead\n"
      + "\n".join(" | ".join(str(x) for x in p) for p in phases))
data["vacuum_phase_names"] = sorted({p[0] for p in raw})

# --------------------------------------------------------------------------- 11. parallel workers
section("11. Workers planned, workers launched",
        "A parallel sequential scan over the 60 MB table, first with the pool free, then with "
        "`max_parallel_workers` reduced so the planner still asks for workers the executor "
        "cannot supply.")
psql("select pg_prewarm('orders');", record=False, tolerate=True)
p1 = psql("explain (analyze, costs off, timing off, summary off) "
          "select count(*) from orders where amount_cents > 0;",
          title="Default: max_parallel_workers_per_gather = 2")
psql("show max_parallel_workers; show max_parallel_workers_per_gather; "
     "show min_parallel_table_scan_size;", title="The pool")
p2 = psql("""set max_parallel_workers_per_gather = 6;
explain (analyze, costs off, timing off, summary off)
select count(*) from orders where amount_cents > 0;""",
          title="Raising max_parallel_workers_per_gather to 6 on its own",
          note="The planner still asks for two. The per-gather setting is a ceiling, not a "
               "request: the number of workers is derived from the table's size.")
psql("alter table orders set (parallel_workers = 6);", record=False)
p3 = psql("""set max_parallel_workers_per_gather = 6;
explain (analyze, costs off, timing off, summary off)
select count(*) from orders where amount_cents > 0;""",
          title="Overriding the derivation with the table's parallel_workers option")
p4 = psql("""set max_parallel_workers_per_gather = 6;
set max_parallel_workers = 1;
explain (analyze, costs off, timing off, summary off)
select count(*) from orders where amount_cents > 0;""",
          title="Six planned, one worker left in the pool")
psql("alter table orders reset (parallel_workers);", record=False)
data["parallel"] = {
    "default": {"planned": num(p1, r"Workers Planned:\s*(\d+)"),
                "launched": num(p1, r"Workers Launched:\s*(\d+)")},
    "guc_raised_only": {"planned": num(p2, r"Workers Planned:\s*(\d+)"),
                        "launched": num(p2, r"Workers Launched:\s*(\d+)")},
    "table_option": {"planned": num(p3, r"Workers Planned:\s*(\d+)"),
                     "launched": num(p3, r"Workers Launched:\s*(\d+)")},
    "starved": {"planned": num(p4, r"Workers Planned:\s*(\d+)"),
                "launched": num(p4, r"Workers Launched:\s*(\d+)")},
}
block(json.dumps(data["parallel"], indent=2))

# the workers, caught in the act
section("11b. The workers, seen from another session")
runner = psycopg.connect(dsn(), autocommit=True)
rc = runner.cursor()
rc.execute("set max_parallel_workers_per_gather = 4")
psql("alter table orders set (parallel_workers = 4);", record=False)
th, _ = in_thread(lambda: rc.execute(
    "select count(*) from orders o1 join orders o2 using (customer_id) "
    "where o1.amount_cents > 99000 and o2.status = 'paid'"))
caught = []
while th.is_alive():                                    # sample until we see the workers
    rows = sample("""select pid, backend_type, leader_pid, state, wait_event_type, wait_event
                     from pg_stat_activity
                     where backend_type in ('client backend','parallel worker')
                       and (leader_pid is not null or pid in
                            (select leader_pid from pg_stat_activity
                             where leader_pid is not null))
                     order by leader_pid nulls first, pid""")
    if len(rows) > len(caught):
        caught = [list(r) for r in rows]
    time.sleep(0.01)
data["parallel_workers_caught"] = caught
block("pid | backend_type | leader_pid | state | wait_event_type | wait_event\n"
      + "\n".join(" | ".join(str(x) for x in r) for r in caught))
th.join()
runner.close()
psql("alter table orders reset (parallel_workers);", record=False)

# --------------------------------------------------------------------------- 12. cancel vs terminate
section("12. Cancel and terminate are two different signals",
        "A session runs `pg_sleep`. `pg_cancel_backend` ends the statement and leaves the "
        "connection alive; `pg_terminate_backend` ends the process. The first arrives as SIGINT, "
        "the second as SIGTERM; both only set a flag that the next `CHECK_FOR_INTERRUPTS()` acts on.")
victim = psycopg.connect(dsn(), autocommit=True)
vc = victim.cursor()
vpid = vc.execute("select pg_backend_pid()").fetchone()[0]
err_cancel = err_term = None
th, sleep_box = in_thread(lambda: vc.execute("select pg_sleep(30)"))
time.sleep(0.4)
q(f"select pg_cancel_backend({vpid})")
th.join(timeout=10)
try:
    vc.execute("select 'still here' as state")
    survived = vc.fetchone()[0]
except Exception as e:                                   # noqa: BLE001
    err_cancel = str(e).strip()
    survived = None
still_alive = sample(f"select count(*) from pg_stat_activity where pid = {vpid}")[0][0]
q(f"select pg_terminate_backend({vpid})")
time.sleep(0.4)
gone = sample(f"select count(*) from pg_stat_activity where pid = {vpid}")[0][0]
try:
    vc.execute("select 1")
except Exception as e:                                   # noqa: BLE001
    err_term = str(e).strip().splitlines()[0]
victim.close()
data["cancel_vs_terminate"] = {
    "backend_pid": vpid,
    "after_cancel_connection_usable": survived,
    "after_cancel_rows_in_pg_stat_activity": still_alive,
    "after_terminate_rows_in_pg_stat_activity": gone,
    "cancel_error": err_cancel or sleep_box.get("error"),
    "terminate_error": err_term,
}
block(json.dumps(data["cancel_vs_terminate"], indent=2, default=str))

# --------------------------------------------------------------------------- 13. wait events
section("13. What a process is waiting on",
        "`pg_stat_activity.wait_event_type` / `wait_event` sampled 200 times a second while a "
        "join runs. This is a sample of instants, not a profile, but it is the cheapest way to "
        "see where time goes.")
runner = psycopg.connect(dsn(), autocommit=True)
rc = runner.cursor()
th, _ = in_thread(lambda: rc.execute(
    "select count(*) from orders o join customers c on c.id = o.customer_id"))
samples = {}
while th.is_alive():
    for bt, wt, we in sample("""select backend_type, coalesce(wait_event_type,'(running)'),
                           coalesce(wait_event,'(cpu)')
                           from pg_stat_activity where state = 'active' or backend_type <> 'client backend'"""):
        samples[(bt, wt, we)] = samples.get((bt, wt, we), 0) + 1
    time.sleep(0.005)
th.join()
runner.close()
top = sorted(samples.items(), key=lambda kv: -kv[1])[:18]
data["wait_events"] = [{"backend_type": k[0], "type": k[1], "event": k[2], "samples": v} for k, v in top]
block("backend_type | wait_event_type | wait_event | samples\n"
      + "\n".join(f"{k[0]} | {k[1]} | {k[2]} | {v}" for k, v in top))

# --------------------------------------------------------------------------- 14. freeze horizon
section("14. How close this cluster is to a wraparound emergency")
psql("""select c.relname,
       age(c.relfrozenxid) as xid_age,
       current_setting('autovacuum_freeze_max_age')::bigint as freeze_max_age,
       current_setting('autovacuum_freeze_max_age')::bigint - age(c.relfrozenxid) as until_forced_vacuum,
       current_setting('vacuum_freeze_min_age')::bigint as freeze_min_age,
       current_setting('vacuum_freeze_table_age')::bigint as freeze_table_age,
       current_setting('vacuum_failsafe_age')::bigint as failsafe_age
from pg_class c
where c.relname in ('customers','orders','vac_demo')
order by 2 desc;""", title="Distance to the anti-wraparound threshold")
data["freeze"] = [list(r) for r in q("""select c.relname, age(c.relfrozenxid)
    from pg_class c where c.relname in ('customers','orders','vac_demo')""")]
psql("""select datname, age(datfrozenxid) as xid_age,
       2147483647 - age(datfrozenxid) as headroom
from pg_database order by 2 desc;""", title="Per-database horizon")

# --------------------------------------------------------------------------- 15. a backend crash
section("15. What the postmaster does when one child dies badly",
        "A backend is killed with SIGKILL. It cannot run its cleanup, so shared memory may be "
        "inconsistent, and the postmaster's only safe move is to terminate every other backend "
        "and run crash recovery. Watch the log.")
obs.close()                                            # the crash below kills every backend
off = log_offset()
crash_victim = psycopg.connect(dsn(), autocommit=True)
cvc = crash_victim.cursor()
cv_pid = cvc.execute("select pg_backend_pid()").fetchone()[0]
bystander = psycopg.connect(dsn(), autocommit=True)
bys_pid = bystander.cursor().execute("select pg_backend_pid()").fetchone()[0]
os.kill(cv_pid, signal.SIGKILL)
time.sleep(3.0)
crash_log = (PGDATA / "server.log").read_text(errors="replace")[off:]
data["crash"] = {
    "killed_pid": cv_pid,
    "bystander_pid": bys_pid,
    "log": crash_log.strip().splitlines(),
}
block(crash_log.strip())
try:
    bystander.cursor().execute("select 1")
    data["crash"]["bystander_survived"] = True
except Exception as e:                                   # noqa: BLE001
    data["crash"]["bystander_survived"] = False
    data["crash"]["bystander_error"] = str(e).strip().splitlines()[0]
for c in (crash_victim, bystander):
    try:
        c.close()
    except Exception:                                    # noqa: BLE001
        pass
md.append(f"The bystander connection (pid {bys_pid}), which was doing nothing wrong, "
          f"{'survived' if data['crash'].get('bystander_survived') else 'was terminated too'}.\n")

# wait for the server to come back
for _ in range(60):
    try:
        q("select 1")
        break
    except Exception:                                    # noqa: BLE001
        time.sleep(0.5)
psql("select pid, backend_type from pg_stat_activity order by backend_type;",
     title="The process list after the automatic restart")

# --------------------------------------------------------------------------- 16. the toolkit
section("16. Cumulative counters for the whole run")
psql("""select checkpoints_timed, checkpoints_req, buffers_checkpoint, buffers_clean,
       maxwritten_clean, buffers_backend, buffers_backend_fsync, buffers_alloc
from pg_stat_bgwriter;""", title="pg_stat_bgwriter", tolerate=True)
psql("""select name, setting from pg_settings
where name like 'autovacuum%' or name like 'vacuum_%' order by name;""",
     title="Every autovacuum and vacuum setting, with its value on this server")
psql("select * from pg_stat_progress_vacuum;", title="pg_stat_progress_vacuum when nothing is running")

# --------------------------------------------------------------------------- done
CAP_MD.write_text("\n".join(md), encoding="utf-8")
CAP_JSON.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
print(f"wrote {CAP_MD} and {CAP_JSON}")
