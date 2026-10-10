#!/usr/bin/env python3
"""Build the finished social package for postgresql-foundations-storage-layer.

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
CANONICAL = "https://canery.in/blogs/postgresql-foundations-storage-layer"

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
u1, u2 = D["update1"], D["update2"]
REC1 = [(r["record_type"], r["record_length"]) for r in u1["wal"] if r["xid"] == str(u1["xid"])]
REC2 = [(r["record_type"], r["record_length"]) for r in u2["wal"]]
W1, W2 = sum(n for _, n in REC1), sum(n for _, n in REC2)
IOS = D["ios"]
CR = D["crash"]
REDO = CR["controldata_after_checkpoint"]["Latest checkpoint's REDO location"]
END = [l for l in CR["server_log"] if "invalid record length" in l][0].split(" at ")[1].split(":")[0]
SW = {(r["kind"], r["raw_bytes"]): r for r in D["toast_sweep"]}
PAGES = D["pages"]["orders"]


# ------------------------------------------------------------------ artefacts (panel content)
def art_three(x, y, w, h, big=False):
    """Data, maps, log — with the lab's real sizes."""
    s = ""
    rows = [("DATA", y + 20), ("MAPS", y + h * 0.43), ("LOG", y + h * 0.74)]
    for lab, yy in rows:
        s += t(x + 32, yy + 26, lab, 15 if not big else 18, SOFT, MONO, "600", track=".16em")
    # data: tile grid
    cols, rws = 14, 3
    tw = 30 if not big else 36
    gx = x + 140
    for r in range(rws):
        for c in range(cols):
            focal = (r, c) == (1, 10)
            s += (f'<rect x="{gx + c * (tw + 8)}" y="{y + 30 + r * (tw + 8)}" width="{tw}" height="{tw}" rx="3" '
                  f'fill="{TINT if focal else "#fff"}" stroke="{ACCENT if focal else SILVER}" stroke-width="{2 if focal else 1.2}"/>')
    yd = y + 30 + rws * (tw + 8) + 28
    s += t(gx, yd, f"heap: {fmt(PAGES)} pages, 63,021,056 bytes", 20 if not big else 24, INK, SANS, "600")
    s += t(gx, yd + 30, "indexes and TOAST chunks: the same 8 KB page format", 17 if not big else 20, MUTED, SANS)
    # maps
    ym = y + h * 0.43 + 8
    s += rect(gx, ym, 26, 26, "rgba(94,122,155,.25)", SLATE)
    s += t(gx + 42, ym + 20, "visibility map: 2 bits per page, 8,192 bytes", 19 if not big else 22, INK, SANS)
    s += rect(gx, ym + 44, 26, 26, "rgba(191,192,192,.35)", SILVER)
    s += t(gx + 42, ym + 64, "free space map: 1 byte per page, 32,768 bytes", 19 if not big else 22, INK, SANS)
    # log
    yl = y + h * 0.74 + 20
    for k in range(64 if not big else 60):
        cx = gx + k * 12
        near = 44 <= k <= 47
        s += f'<circle cx="{cx}" cy="{yl}" r="{3.4 if near else 2.4}" fill="{ACCENT if near else "rgba(45,49,66,.45)"}"/>'
    s += t(gx, yl + 40, "WAL: 16 MiB segment files, every change in order", 19 if not big else 22, INK, SANS)
    return s


def art_updates(x, y, w, h, big=False):
    s = ""
    scale = (w - 120) / W1
    cols = {"LOCK": SLATE, "UPDATE": INK, "INSERT_LEAF": "#7c8f6f", "COMMIT": SOFT, "HOT_UPDATE": ACCENT}
    blocks = [("update 1 · not HOT", REC1, W1, "4 pages: both heap pages, one leaf in each index", y + 50),
              ("update 2 · HOT", REC2, W2, "1 page: heap page 7692", y + h * 0.52)]
    for label, recs, total, pages, yy in blocks:
        hot = "HOT" in label and "not" not in label
        s += t(x + 40, yy, label, 24 if not big else 28, ACCENT if hot else INK, SANS, "600")
        xx = x + 40
        for name, n in recs:
            c = cols[name]
            s += (f'<rect x="{xx}" y="{yy + 22}" width="{n * scale}" height="{64 if not big else 80}" '
                  f'fill="{c}" fill-opacity=".30" stroke="{c}" stroke-width="1.4"/>')
            if n * scale > 60:
                s += t(xx + n * scale / 2, yy + 52, name, 14 if n * scale > 110 else 12, INK, MONO, "500", "middle")
                s += t(xx + n * scale / 2, yy + 74, f"{n} B", 16, INK, MONO, "600", "middle")
            xx += n * scale
        s += t(x + 40, yy + (118 if not big else 136), f"{total} bytes · {len(recs)} records · {pages}", 18 if not big else 21, MUTED, SANS)
    s += t(x + 40, y + h - 36, f"page 32 had {D['free_bytes_on_page']} bytes free; the new version needed 60", 18 if not big else 21, ACCENT, MONO, "500")
    return s


def art_vm(x, y, w, h, big=False):
    s = ""
    bx, bw = x + 40, w - 80
    k = bw / PAGES
    by = y + 80
    s += t(bx, by - 22, f"the all-visible bit of each of {fmt(PAGES)} pages", 18 if not big else 21, MUTED, SANS)
    s += f'<rect x="{bx}" y="{by}" width="{bw}" height="70" rx="4" fill="rgba(94,122,155,.28)" stroke="{SLATE}"/>'
    for p in (32, PAGES - 1):
        s += f'<rect x="{bx + p * k - 3}" y="{by - 10}" width="6" height="90" fill="{ACCENT}"/>'
    s += t(bx + 32 * k, by + 110, "page 32", 16, ACCENT, MONO, "600", "start")
    s += t(bx + bw, by + 110, "page 7692", 16, ACCENT, MONO, "600", "end")
    s += t(bx, by + 170, "only these two pages had anything to clean", 20 if not big else 24, INK, SANS, "600")
    vy = y + h * 0.55
    s += rect(bx, vy, bw, 150 if not big else 190, "#f5f5f5", SILVER, 6)
    s += t(bx + 24, vy + 44, "VACUUM (VERBOSE) orders", 18 if not big else 21, SOFT, MONO, "500")
    s += t(bx + 24, vy + 86, "pages: 0 removed, 7693 remain,", 22 if not big else 26, INK, MONO, "500")
    s += t(bx + 24, vy + 122 if not big else vy + 128, "2 scanned (0.03% of total)", 22 if not big else 26, ACCENT, MONO, "600")
    return s


def art_ios(x, y, w, h, big=False):
    s = ""
    runs = [("all-visible", IOS["clean"]), ("1 row in 50\nupdated", IOS["dirty"]), ("after vacuum", IOS["vacuumed"])]
    base = y + h - 170
    top = y + 90
    vmax = 110000
    colw = (w - 80) / 3
    s += t(x + 40, y + 50, "heap fetches in EXPLAIN (ANALYZE, BUFFERS)", 18 if not big else 21, MUTED, SANS)
    for i, (lab, r) in enumerate(runs):
        cx = x + 40 + i * colw + colw / 2
        v = r["heap_fetches"]
        hh = max(v / vmax * (base - top), 3)
        focal = i == 1
        s += (f'<rect x="{cx - 70}" y="{base - hh}" width="140" height="{hh}" rx="4" '
              f'fill="{ACCENT if focal else SLATE}" fill-opacity="{.55 if focal else .45}" stroke="{ACCENT if focal else SLATE}"/>')
        s += t(cx, base - hh - 16, fmt(v), 30 if not big else 34, INK, MONO, "600", "middle")
        for j, ln in enumerate(lab.split("\n")):
            s += t(cx, base + 36 + j * 26, ln, 19 if not big else 22, INK, SANS, "500", "middle")
        s += t(cx, base + 100, f"{fmt(r['shared_hit'] + r['shared_read'])} buffers", 17 if not big else 20, SOFT, MONO, "500", "middle")
    return s


def art_toast(x, y, w, h, big=False):
    s = ""
    rows = [("value size", "compressible text", "hex text (won't compress)"),
            ("2,000 B", f"inline · {SW[('compressible', 2000)]['bytes_in_row']:,} B", f"inline · {SW[('incompressible', 2000)]['bytes_in_row']:,} B"),
            ("2,001 B", f"{SW[('compressible', 2001)]['bytes_in_row']} B · pglz", "18 B pointer · 2 chunks"),
            ("10,000 B", f"{SW[('compressible', 10000)]['bytes_in_row']} B · pglz", "18 B pointer · 6 chunks")]
    cx = [x + 40, x + 250, x + 590]
    rh = (h - 160) / 4
    for i, row in enumerate(rows):
        yy = y + 70 + i * rh
        head = i == 0
        if i:
            s += f'<line x1="{x + 30}" y1="{yy - rh / 2 - 6}" x2="{x + w - 30}" y2="{yy - rh / 2 - 6}" stroke="{RULE}"/>'
        for j, cell in enumerate(row):
            hot = (i == 2) or (i == 3 and j == 2)
            col = SOFT if head else (ACCENT if hot and j > 0 else INK)
            s += t(cx[j], yy, cell, (17 if head else 22) if not big else (20 if head else 26), col,
                   MONO if not head else MONO, "600" if not head and j == 0 else "500")
    s += t(x + 40, y + h - 40, "the toaster wakes when the row passes 2,032 bytes", 18 if not big else 21, MUTED, SANS)
    return s


def art_crash(x, y, w, h, big=False):
    s = ""
    lines = [("before the crash, in memory", f"pd_lsn {CR['page_lsn_memory']}", INK),
             ("the same page in the table file", f"pd_lsn {CR['page_lsn_disk_while_down']}", ACCENT),
             ("restart: redo starts at", REDO, INK),
             ("end of WAL", f"zero-length record at {END}", INK),
             ("after replay, the table file", f"pd_lsn {CR['page_lsn_disk_after_recovery']} · amount 60000", INK)]
    step = (h - 80) / len(lines)
    for i, (lab, val, col) in enumerate(lines):
        yy = y + 60 + i * step
        s += t(x + 40, yy, lab, 18 if not big else 21, SOFT, SANS)
        s += t(x + 40, yy + (34 if not big else 40), val, 24 if not big else 28, col, MONO, "600")
        if i < len(lines) - 1:
            ax = x + w - 60
            s += (f'<line x1="{ax}" y1="{yy + 8}" x2="{ax}" y2="{yy + step - 30}" stroke="{SILVER}" stroke-width="1.4"/>'
                  f'<polygon points="{ax - 6},{yy + step - 32} {ax + 6},{yy + step - 32} {ax},{yy + step - 22}" fill="{SILVER}"/>')
    return s


# ------------------------------------------------------------------ the cards
FEED = [
    dict(stem="feed-01-data-maps-log", title="What PostgreSQL keeps on disk", role="cover",
         setup="Data, two maps of the data, and one log. One real row shows all three.",
         take="Every storage surprise is one of these three doing its job.", art=art_three,
         beat="Everything on disk is data, a map of the data, or the log.",
         source="Intuition section; Figure 2 and Figure 4; ledger L02",
         structure="Headline and setup at top; a panel with three labelled rows (data tiles, two map strips, a dotted log line) with sizes; takeaway and footer below.",
         transcript=f"What PostgreSQL keeps on disk · Data, two maps of the data, and one log. One real row shows all three. · DATA · heap: {fmt(PAGES)} pages, 63,021,056 bytes · indexes and TOAST chunks: the same 8 KB page format · MAPS · visibility map: 2 bits per page, 8,192 bytes · free space map: 1 byte per page, 32,768 bytes · LOG · WAL: 16 MiB segment files, every change in order · Every storage surprise is one of these three doing its job. · POSTGRESQL FOUNDATIONS · PART 3 · CANERY.IN",
         alt="PostgreSQL's on-disk storage as three kinds: a 7,693-page heap, two small map forks of 8 and 32 KB, and a log of 16 MiB segments.",
         longdesc="Cover card for the storage-layer article. A grid of page tiles stands for the orders heap, 7,693 pages or 63,021,056 bytes, with one tile highlighted as the page that changes. Two small squares stand for the visibility map (2 bits per heap page, 8,192 bytes) and the free space map (1 byte per heap page, 32,768 bytes). A dotted line stands for the write-ahead log, stored as 16 MiB segment files. The takeaway: every storage-layer surprise is one of these three structures doing its job.",
         keywords="PostgreSQL, storage layer, heap, visibility map, free space map, WAL"),
    dict(stem="feed-02-not-hot", title="Same change, three times the log", role="technical",
         setup="Two status updates to one row of orders. The first could not stay on its page.",
         take="HOT needs an unindexed change and room on the same page.", art=art_updates,
         beat="The first update was not HOT because its page was full; the second was.",
         source="HOT section; Figure 10; ledger L07, L10",
         structure="Headline and setup; two stacked horizontal bars split into WAL records, to scale; a line naming the free space on page 32; takeaway.",
         transcript=f"Same change, three times the log · Two status updates to one row of orders. The first could not stay on its page. · update 1 · not HOT · LOCK 54 B · UPDATE 106 B · INSERT_LEAF 64 B · INSERT_LEAF 64 B · {W1} bytes · 5 records · 4 pages: both heap pages, one leaf in each index · update 2 · HOT · HOT_UPDATE 77 B · {W2} bytes · 2 records · 1 page: heap page 7692 · page 32 had 24 bytes free; the new version needed 60 · HOT needs an unindexed change and room on the same page.",
         alt=f"Two WAL bars for the same status update: {W1} bytes in five records across four pages when not HOT, {W2} bytes in two records when HOT.",
         longdesc=f"Two updates changed the unindexed status column of row 4242. The first found only 24 bytes free on page 32, so its new version went to page 7692 and needed a new entry in both indexes: LOCK 54 B, UPDATE 106 B, two INSERT_LEAF records of 64 B, and COMMIT 34 B, {W1} bytes in five records touching four pages. The second update found room on page 7692 and was HOT: HOT_UPDATE 77 B and COMMIT 34 B, {W2} bytes on one page. PostgreSQL 16.2, lab measurement.",
         keywords="PostgreSQL, HOT update, heap-only tuple, WAL, fillfactor, indexes"),
    dict(stem="feed-03-two-pages", title="Vacuum read 2 of 7,693 pages", role="technical",
         setup="The visibility map told it the other 7,691 pages had nothing to clean.",
         take="Two bits per page decide how much vacuum has to read.", art=art_vm,
         beat="The visibility map lets vacuum skip every all-visible page.",
         source="The visibility map section; Figure 11; ledger L14, L60",
         structure="Headline and setup; a long band for the table's pages with two tangerine ticks; a monospace box quoting VACUUM VERBOSE; takeaway.",
         transcript=f"Vacuum read 2 of 7,693 pages · The visibility map told it the other 7,691 pages had nothing to clean. · the all-visible bit of each of {fmt(PAGES)} pages · page 32 · page 7692 · only these two pages had anything to clean · VACUUM (VERBOSE) orders · pages: 0 removed, 7693 remain, 2 scanned (0.03% of total) · Two bits per page decide how much vacuum has to read.",
         alt="A band of 7,693 visibility-map bits with only pages 32 and 7692 clear, and VACUUM VERBOSE reporting 2 pages scanned.",
         longdesc="After two updates, only heap pages 32 and 7692 of the orders table had their visibility-map all-visible bit cleared. VACUUM (VERBOSE) reported: pages: 0 removed, 7693 remain, 2 scanned (0.03% of total). The visibility map keeps two bits per heap page, all-visible and all-frozen, set only by vacuum and cleared by any change. Vacuum skips runs of 32 or more all-visible pages.",
         keywords="PostgreSQL, vacuum, visibility map, all-visible, VACUUM VERBOSE"),
    dict(stem="feed-04-heap-fetches", title="102,000 visits to the heap", role="technical",
         setup="The same index-only count, before and after one row in fifty was updated.",
         take="Heap Fetches in EXPLAIN is the visibility map's report card.", art=art_ios,
         beat="An index-only scan visits the heap for every page the visibility map does not mark all-visible.",
         source="The visibility map section; Figure 12; ledger L34",
         structure="Headline and setup; three vertical bars of heap fetches with buffer counts beneath; takeaway.",
         transcript=f"102,000 visits to the heap · The same index-only count, before and after one row in fifty was updated. · heap fetches in EXPLAIN (ANALYZE, BUFFERS) · 0 · all-visible · 118 buffers · 102,000 · 1 row in 50 updated · 102,118 buffers · 0 · after vacuum · 118 buffers · Heap Fetches in EXPLAIN is the visibility map's report card.",
         alt="Heap fetches for one index-only count: 0 when all-visible, 102,000 after updating one row in fifty, and 0 again after vacuum.",
         longdesc="An index-only count of 100,000 rows on a 7,847-page copy of orders, run three times with the plan forced to an index-only scan. With every page all-visible it fetched 0 heap tuples and touched 118 buffers. After updating one row in fifty, which cleared the visibility bit on every page, it made 102,000 heap fetches and touched 102,118 buffers. After vacuum it was back to 0 fetches and 118 buffers. PostgreSQL 16.2.",
         keywords="PostgreSQL, index-only scan, Heap Fetches, visibility map, EXPLAIN"),
    dict(stem="feed-05-toast-cliff", title="2,000 bytes stays. 2,001 leaves.", role="technical",
         setup="A row wider than 2,032 bytes wakes the toaster. Then it depends on the text.",
         take="Compress by a quarter and stay; otherwise leave an 18-byte pointer.", art=art_toast,
         beat="TOAST compresses or moves values once a row passes 2,032 bytes.",
         source="TOAST section; Figure 14 and Figure 15; ledger L17, L18",
         structure="Headline and setup; a three-row table of value size against what compressible and incompressible text become; takeaway.",
         transcript="2,000 bytes stays. 2,001 leaves. · A row wider than 2,032 bytes wakes the toaster. Then it depends on the text. · value size · compressible text · hex text (won't compress) · 2,000 B · inline · 2,004 B · inline · 2,004 B · 2,001 B · 51 B · pglz · 18 B pointer · 2 chunks · 10,000 B · 142 B · pglz · 18 B pointer · 6 chunks · the toaster wakes when the row passes 2,032 bytes · Compress by a quarter and stay; otherwise leave an 18-byte pointer.",
         alt="What a text value becomes in its row: 2,000 bytes stays inline; at 2,001 it compresses to 51 bytes or leaves an 18-byte pointer.",
         longdesc="Measured on an (int, text) table in PostgreSQL 16.2. A 2,000-byte value makes a 2,032-byte row and stays inline. At 2,001 bytes the toaster runs: compressible text becomes 51 bytes of pglz output inline, and hex text, which pglz cannot shrink by the required 25%, moves out of line behind an 18-byte pointer in two chunks. At 10,000 bytes compressible text is 142 bytes inline; hex text is six chunks of at most 1,996 bytes.",
         keywords="PostgreSQL, TOAST, pglz, TOAST pointer, chunks, varlena"),
    dict(stem="feed-06-only-in-the-log", title="The change was only in the log", role="cta",
         setup="A commit, then a crash. The table file was still one change behind.",
         take="Read the whole walk-through, byte by byte, on canery.in", art=art_crash,
         beat="Crash recovery replays WAL from the checkpoint's REDO point onto pages that missed it.",
         source="Crash recovery section; Figure 20; ledger L29–L31",
         structure="Headline and setup; five stacked monospace facts joined by arrows from before the crash to after replay; call to action.",
         transcript=f"The change was only in the log · A commit, then a crash. The table file was still one change behind. · before the crash, in memory · pd_lsn {CR['page_lsn_memory']} · the same page in the table file · pd_lsn {CR['page_lsn_disk_while_down']} · restart: redo starts at · {REDO} · end of WAL · zero-length record at {END} · after replay, the table file · pd_lsn {CR['page_lsn_disk_after_recovery']} · amount 60000 · Read the whole walk-through, byte by byte, on canery.in",
         alt="Crash replay in five lines: page LSN in memory ahead of the file, redo from the REDO point, end of WAL, file caught up.",
         longdesc=f"After a committed update and an immediate shutdown, page 7692 in memory carried pd_lsn {CR['page_lsn_memory']}, while the same page in the table file still said {CR['page_lsn_disk_while_down']} and had one line pointer fewer. On restart the startup process replayed WAL from the checkpoint's REDO location {REDO}, stopped at a zero-length record at {END}, and the end-of-recovery checkpoint wrote the page: its file copy then read {CR['page_lsn_disk_after_recovery']} and the row's amount was 60000. Call to action to read the article.",
         keywords="PostgreSQL, crash recovery, WAL, REDO, pd_lsn, LSN"),
]

STORY = [
    dict(stem="story-01-data-maps-log", title="What PostgreSQL keeps on disk", role="cover",
         setup="Data, two maps, and a log.", take="One real row, followed byte by byte.", art=art_three,
         overlay="Everything on disk is data, a map, or the log",
         beat="Story opener: the three kinds of on-disk structure, each with its real size.", source=FEED[0]["source"],
         structure="Hook headline, setup line, a tall panel with the three labelled groups and their sizes, takeaway, footer.",
         transcript=f"What PostgreSQL keeps on disk · Data, two maps, and a log. · DATA · heap: {fmt(PAGES)} pages, 63,021,056 bytes · indexes and TOAST chunks: the same 8 KB page format · MAPS · visibility map: 2 bits per page, 8,192 bytes · free space map: 1 byte per page, 32,768 bytes · LOG · WAL: 16 MiB segment files, every change in order · One real row, followed byte by byte. · POSTGRESQL FOUNDATIONS · PART 3 · CANERY.IN",
         alt="Story cover: PostgreSQL's on-disk storage as heap pages, two small map forks of 8 and 32 KB, and a log of 16 MiB segment files.",
         longdesc="Story cover, recomposed for 9:16. Three labelled groups fill a tall panel: page tiles for the 7,693-page orders heap (63,021,056 bytes) with one highlighted, two small squares for the visibility map (8,192 bytes, 2 bits per page) and the free space map (32,768 bytes, 1 byte per page), and a dotted line for the write-ahead log in 16 MiB segments. The frame promises one real row followed byte by byte.",
         keywords=FEED[0]["keywords"]),
    dict(stem="story-02-not-hot", title="Same change, three times the log", role="technical",
         setup="The first update could not stay on its page.", take="HOT needs room on the same page.", art=art_updates,
         overlay="Why the first update wrote to both indexes",
         beat="Story beat: a full page forced the first update off its page and into both indexes.", source=FEED[1]["source"], structure=FEED[1]["structure"],
         transcript=f"Same change, three times the log · The first update could not stay on its page. · update 1 · not HOT · LOCK 54 B · UPDATE 106 B · INSERT_LEAF 64 B · INSERT_LEAF 64 B · {W1} bytes · 5 records · 4 pages: both heap pages, one leaf in each index · update 2 · HOT · HOT_UPDATE 77 B · {W2} bytes · 2 records · 1 page: heap page 7692 · page 32 had 24 bytes free; the new version needed 60 · HOT needs room on the same page.",
         alt=f"Story frame: the first status update cost {W1} bytes of WAL on four pages, the HOT one {W2} bytes on one page.",
         longdesc=f"Story version of the update comparison. The non-HOT update of row 4242 wrote LOCK, UPDATE, two INSERT_LEAF records and COMMIT, {W1} bytes on two heap pages and one leaf of each index, because page 32 had only 24 bytes free. The HOT update wrote HOT_UPDATE and COMMIT, {W2} bytes on heap page 7692 alone. Lab measurement on PostgreSQL 16.2.",
         keywords=FEED[1]["keywords"]),
    dict(stem="story-03-two-pages", title="Vacuum read 2 of 7,693 pages", role="technical",
         setup="The visibility map skipped the rest.", take="Two bits per page decide what vacuum reads.", art=art_vm,
         overlay="2 of 7,693 pages: the visibility map at work",
         beat="Story beat: two clear visibility bits, two pages read by vacuum.", source=FEED[2]["source"], structure=FEED[2]["structure"],
         transcript=f"Vacuum read 2 of 7,693 pages · The visibility map skipped the rest. · the all-visible bit of each of {fmt(PAGES)} pages · page 32 · page 7692 · only these two pages had anything to clean · VACUUM (VERBOSE) orders · pages: 0 removed, 7693 remain, 2 scanned (0.03% of total) · Two bits per page decide what vacuum reads.",
         alt="Story frame: the table's 7,693 visibility bits drawn as a band with two clear, and vacuum reporting 2 pages scanned.",
         longdesc="Story version of the vacuum result. A band stands for all 7,693 visibility-map bits of orders; only the bits for pages 32 and 7692 are clear, because only those pages changed. A monospace box quotes VACUUM (VERBOSE): 0 pages removed, 7693 remain, 2 scanned, 0.03% of the table. The takeaway: the map's two bits per page decide what vacuum reads.",
         keywords=FEED[2]["keywords"]),
    dict(stem="story-04-only-in-the-log", title="The change was only in the log", role="cta",
         setup="And the log was enough.", take="Read the article: link sticker below.", art=art_crash,
         overlay="Nothing committed was lost. Read how →",
         beat="Story close: nothing committed was lost, and the link to the article.", source=FEED[5]["source"], structure=FEED[5]["structure"].replace("call to action", "call to action and a link sticker area"),
         transcript=f"The change was only in the log · And the log was enough. · before the crash, in memory · pd_lsn {CR['page_lsn_memory']} · the same page in the table file · pd_lsn {CR['page_lsn_disk_while_down']} · restart: redo starts at · {REDO} · end of WAL · zero-length record at {END} · after replay, the table file · pd_lsn {CR['page_lsn_disk_after_recovery']} · amount 60000 · Read the article: link sticker below. · POSTGRESQL FOUNDATIONS · PART 3 · CANERY.IN",
         alt="Story close: crash replay in five lines, page LSN in memory ahead of the file, then replayed from the REDO point until caught up.",
         longdesc=f"Story close, recomposed for 9:16. Five stacked facts from the lab's crash: the page's LSN in memory ({CR['page_lsn_memory']}) ahead of its file copy ({CR['page_lsn_disk_while_down']}); replay starting at the REDO point {REDO}; the log ending at a zero-length record at {END}; and the file caught up at {CR['page_lsn_disk_after_recovery']} with the committed amount of 60000. The frame leaves room for the link sticker to the article.",
         keywords=FEED[5]["keywords"]),
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
        t(72, fy, "POSTGRESQL FOUNDATIONS · PART 3 · CANERY.IN", 14 if feed else 16, ACCENT, MONO, "500", track=".14em"),
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

# Social publishing package — postgresql-foundations-storage-layer

## LinkedIn post

I followed one row of a PostgreSQL table from its first byte to crash recovery, on a real server.

Two updates changed the same unindexed column. The first could not stay on its page (24 bytes free), so it wrote {W1} bytes of WAL and a new entry in both indexes. The second was HOT: {W2} bytes, no index touched.

Vacuum then read 2 of the table's 7,693 pages, because the visibility map said the rest were clean. The same map turned an index-only count into 102,000 heap fetches until vacuum set it again.

A 2,000-byte value stayed in its row; 2,001 bytes did not. And after an immediate shutdown, the committed change existed only in the write-ahead log, which was enough.

Part 3 of PostgreSQL Foundations, the storage layer. Swipe through the six cards; the link is in the first comment.

## LinkedIn first comment

Everything PostgreSQL keeps on disk is data, a map of the data, or the log, and every one of the surprises above is one of those three doing its job.

Read the full article on Canery: {CANONICAL}

## Instagram caption

One PostgreSQL row, followed byte by byte: a non-HOT update that paid for both indexes, a vacuum that read 2 pages of 7,693, a 2,001-byte value that left its row, and a crash that lost nothing because the log had it. Part 3 of PostgreSQL Foundations, the storage layer. Full article on canery.in, link in bio.

## Shared feed order

{feed_order}

## Instagram Story

- CTA: Read how PostgreSQL stores a row, and gets it back after a crash
- Link sticker label: Read the article
- Link sticker URL: {CANONICAL}

### Story order

{story_order}

## Asset metadata

""" + "\n".join(meta_block(c, "feed") for c in FEED) + "\n" + "\n".join(meta_block(c, "story") for c in STORY)
    (POST / "social.md").write_text(md, encoding="utf-8")
    print(f"  social: {len(FEED)} feed + {len(STORY)} story sources, social.md")


if __name__ == "__main__":
    build()
