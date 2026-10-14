#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for "Hash Map, Sorted Array or Tree? When Each
Pays for Itself".

Search Algorithms, part 2. The shell (lockup, rule, serif title, deck, takeaway, footer) is copied
from image-processing part 11's _social.py, with the lockup reading "canery.in". Every number on a
card comes from `_data.py`, which reads the lab's captures.json and asserts each value against the
article, so a card cannot disagree with the article. Colours follow the figures: tangerine for the
sorted side and red nodes, blue for search paths and the hash side.

Lockup widths are 220 (feed) and 245 (story), which render_social.py locks.
This script writes editable HTML only; Blog Forge's render_social.py exports the
standalone SVG and exact-size PNG:

    python3 _social.py
    python3 ../../../../.claude/blog-forge/scripts/render_social.py social/
"""

from __future__ import annotations

import html
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "social"
ROOT = HERE.parents[3]                     # a series member sits one level deeper
sys.path.insert(0, str(HERE))
import _data as d  # noqa: E402  — the article's numbers and conventions

VW = 1080
PAPER = "#f5f5f5"
INK = "#2d3142"
MUTED = "#4f5d75"
SOFT = "#7a8399"
RULE = "rgba(45,49,66,0.14)"
RULE_SOLID = "#bfc0c0"
ACCENT = "#eb6c36"
ACCENT_TINT = "rgba(235,108,54,0.08)"
LINK = "#2e5aa8"                            # the figures' blue, so cards and figures match
GREEN, MUSTARD = "#7c8f6f", "#b8915a"
SANS = "'Geist',system-ui,sans-serif"
SERIF = "'Instrument Serif',Georgia,serif"
MONO = "'Geist Mono',ui-monospace,monospace"
FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
         "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap")
CANONICAL = "canery.in/blogs/when-a-search-structure-pays-for-itself"
FOOTER = "SEARCH ALGORITHMS, PART 2 · CANERY.IN"

# ------------------------------------------------------------------ the lockup
LOCKUP_VIEWBOX_W = 671.40
IN_GAP = -10
IN_SIZE = 140
IN_ADVANCE = 171
LOCKUP_FULL_W = LOCKUP_VIEWBOX_W + IN_GAP + IN_ADVANCE


def logo_paths() -> str:
    source = (ROOT / "web/public/brand/canerly-lockup-horizontal.svg").read_text(encoding="utf-8")
    paths = re.findall(r"<path\b[\s\S]*?/>", source)
    if len(paths) != 2:
        raise RuntimeError("Could not read the canonical Canery horizontal lockup")
    suffix = (f'<text x="{LOCKUP_VIEWBOX_W + IN_GAP}" y="122.5" font-size="{IN_SIZE}" '
              f'font-family="{SANS}" font-weight="600" text-anchor="start">.in</text>')
    return "\n".join(paths) + "\n" + suffix


LOGO_PATHS = logo_paths()


# ------------------------------------------------------------------ primitives
def esc(v) -> str:
    return html.escape(str(v), quote=True)


def ascii_upper(v) -> str:
    return "".join(c.upper() if "a" <= c <= "z" else c for c in str(v))


def txt(x, y, value, size=22, fill=INK, family=SANS, weight=400, anchor="start", track=None):
    extra = f' letter-spacing="{track}"' if track else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}"{extra}>{esc(value)}</text>')


def mono(x, y, value, size=18, fill=INK, anchor="start", weight=400):
    return txt(x, y, value, size, fill, MONO, weight, anchor)


def label(x, y, value, fill=SOFT, anchor="start", size=14):
    return txt(x, y, ascii_upper(value), size, fill, MONO, 500, anchor, "0.12em")


def lines(x, y, values, size, family=SANS, fill=INK, weight=400, gap=None, anchor="start"):
    gap = gap or int(size * 1.16)
    return "".join(txt(x, y + i * gap, v, size, fill, family, weight, anchor)
                   for i, v in enumerate(values))


def box(x, y, w, h, fill="#ffffff", stroke="rgba(45,49,66,0.28)", rx=8, sw=1):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')


def rect(x, y, w, h, fill, stroke="none", sw=0, op=None, dash=None):
    o = f' fill-opacity="{op}"' if op is not None else ""
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{o} stroke="{stroke}" '
            f'stroke-width="{sw}"{dd}/>')


def line(x1, y1, x2, y2, stroke=INK, sw=2, dash=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{dd}/>'


def hline(x1, x2, y, stroke=RULE, sw=1, dash=None):
    return line(x1, y, x2, y, stroke, sw, dash)


def blend(rgb, a, paper=(255, 255, 255)):
    rr, gg, bb = (round(a * c + (1 - a) * p) for c, p in zip(rgb, paper))
    return f"#{rr:02x}{gg:02x}{bb:02x}"


# ------------------------------------------------------------------ the shell
def shell(kind, number, total, title, deck, visual, takeaway, cta=None):
    if kind == "feed":
        height, logo_y, logo_w = 1350, 72, 220
        rule_y, title_y, title_size, title_gap = 150, 245, 58, 66
        deck_y = title_y + len(title) * title_gap + 20
        take_rule, take_y, foot_y = 1168, 1220, 1305
    else:
        height, logo_y, logo_w = 1920, 250, 245
        rule_y, title_y, title_size, title_gap = 340, 470, 70, 80
        deck_y = title_y + len(title) * title_gap + 28
        take_rule, take_y, foot_y = 1505, 1570, 1665
    scale = logo_w / LOCKUP_FULL_W
    defs = f'<defs><style>@import url(\'{FONTS.replace("&", "&amp;")}\');</style></defs>'
    body = f'<rect width="{VW}" height="{height}" fill="{PAPER}"/>'
    body += (f'<g data-canery-logo="lockup" data-logo-x="72" data-logo-y="{logo_y}" '
             f'data-logo-width="{logo_w}" fill="{INK}" '
             f'transform="translate(72 {logo_y}) scale({scale})">{LOGO_PATHS}</g>')
    body += label(1008, logo_y + 35, f"{number:02d} / {total:02d}", SOFT, "end", 15)
    body += hline(72, 1008, rule_y)
    body += lines(72, title_y, title, title_size, SERIF, gap=title_gap)
    body += lines(72, deck_y, deck, 22 if kind == "feed" else 26, fill=MUTED,
                  gap=30 if kind == "feed" else 36)
    body += visual
    body += hline(72, 1008, take_rule)
    body += lines(72, take_y, takeaway, 22 if kind == "feed" else 27, weight=600,
                  gap=30 if kind == "feed" else 36)
    body += label(72, foot_y, cta or FOOTER, ACCENT if cta else SOFT, "start",
                  14 if kind == "feed" else 16)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VW} {height}" '
            f'width="{VW}" height="{height}" role="img">\n{defs}\n{body}\n</svg>')


def emit(kind, number, slug, title, deck, visual, takeaway, total, cta=None):
    svg = shell(kind, number, total, title, deck, visual, takeaway, cta)
    page = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<title>{esc(" ".join(title))}</title><link href="{FONTS.replace("&", "&amp;")}" rel="stylesheet">'
            f'<style>html,body{{margin:0;background:{PAPER}}}svg{{display:block}}</style>'
            f'</head><body>{svg}</body></html>')
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{kind}-{number:02d}-{slug}.html"
    path.write_text(page, encoding="utf-8")
    print(path.name)


# ------------------------------------------------------------------ the numbers
FEED_TOTAL, STORY_TOTAL = 8, 4
SCAN, BIN, WORST, MEAN = d.SCAN_HIT, d.BIN_HIT, d.SORT_WORST, d.SORT_MEAN
SAVE = SCAN - BIN
Q, QM, QMISS = d.Q_WORST, d.Q_MEAN, d.Q_MISS
FIRST = d.BE["hits_worst_sort"]["first_q_ahead"]
BIG = d.SCALE_ROWS[-1]
I50, T50 = d.INS, d.TM["insert_50"]
ARR = dict(d.writes(1.0, "array"))
TREE = dict(d.writes(1.0, "tree"))
COLL = d.COLL["insert_eq_calls"]
assert (WORST, round(Q, 2), FIRST, round(BIG["q_hits"], 2), BIG["n"]) == (49, 9.56, 10, 38.0, 1 << 20)


def fv(v, nd=1):
    return f"{v:,.{nd}f}" if abs(v - round(v)) > 1e-9 else f"{round(v):,}"


def about(v):
    """Round to tens, as the article does: 1,770.5 is "about 1,770"."""
    return f"{round(v, -1):,.0f}"


def dot(x, y, r_, fill):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r_}" fill="{fill}"/>'


def crossing(x, y, w, h, label_size=19, qmax=20, vmax=180):
    """Figure 1, simplified: the scan line against sort-then-search, the crossing in tangerine."""
    X = lambda q: x + w * q / qmax
    Y = lambda v: y + h - h * v / vmax
    s = line(x, y + h, x + w, y + h, MUTED, 1.5) + line(x, y, x, y + h, MUTED, 1.5)
    s += line(X(0), Y(0), X(qmax), Y(qmax * SCAN), INK, 4)
    s += line(X(0), Y(WORST), X(qmax), Y(WORST + qmax * BIN), MUTED, 4)
    s += dot(X(Q), Y(SCAN * Q), 11, ACCENT)
    s += mono(X(15) - 12, Y(15 * SCAN) - 16, "scan", label_size, INK, "end", 600)          # above-left of a steep line
    s += mono(X(qmax), Y(WORST + qmax * BIN) + 4.2 * label_size, "sort, then search", label_size, MUTED, "end", 600)
    s += mono(X(Q) + 22, Y(SCAN * Q) + 46, f"cross at {fv(Q, 2)} lookups", label_size, ACCENT, "start", 600)
    s += mono(x + 8, Y(WORST) - 0.8 * label_size, f"{WORST}", label_size - 2, MUTED, "start", 600)
    s += mono(x, y + h + 34, f"0 to {qmax} lookups", label_size - 2, SOFT)
    return s


def array_strip(x, y, cw, ch, keys, moved=(), new=None, size=20, path=()):
    s = ""
    for i, k in enumerate(keys):
        if k == new:
            s += rect(x + i * cw, y, cw, ch, ACCENT, ACCENT, 1.5)
            s += mono(x + i * cw + cw / 2, y + ch / 2 + 7, str(k), size, "#ffffff", "middle", 600)
            continue
        hot = k in moved
        s += rect(x + i * cw, y, cw, ch, blend((235, 108, 54), 0.12) if hot else "#ffffff",
                  ACCENT if hot else "rgba(45,49,66,0.35)", 1.5 if hot else 1)
        s += mono(x + i * cw + cw / 2, y + ch / 2 + 7, str(k), size, INK, "middle", 500)
    return s


def mini_tree(x, y, dx, dy, r_=17, size=14):
    """TreeMap's tree after inserting 50, laid out as Figure 2 (in-order x, depth y), path in blue."""
    nodes = []

    def walk(t, depth):
        if t is None:
            return
        walk(t[2], depth + 1)
        nodes.append((t[0], t[1], depth, t[2][0] if t[2] else None, t[3][0] if t[3] else None))
        walk(t[3], depth + 1)
    walk(d.TREE_AFTER, 0)
    pos = {k: (x + i * dx, y + dep * dy) for i, (k, _, dep, _, _) in enumerate(nodes)}
    on_path = set(zip(d.PATH_50, d.PATH_50[1:] + [50]))
    s = ""
    for k, _, _, lc, rc in nodes:
        for c in (lc, rc):
            if c is not None:
                hot = (k, c) in on_path
                s += line(*pos[k], *pos[c], LINK if hot else RULE_SOLID, 5 if hot else 1.5)
    for k, col, _, _, _ in nodes:
        px, py = pos[k]
        s += dot(px, py, r_, INK if col == "black" else ACCENT)
        s += mono(px, py + size * 0.36, str(k), size, "#ffffff", "middle", 600)
    return s


def bar_rows(x, y, rows, w, colour, size=21, gap=62, vmax=None, fmt=fv):
    vmax = vmax or max(v for _, v in rows)
    s = ""
    for i, (lab, v) in enumerate(rows):
        yy = y + i * gap
        bw = max(4, w * v / vmax)
        s += mono(x, yy + 22, lab, size, INK, "start", 500)
        s += rect(x + 170, yy, bw, 30, colour)
        s += mono(x + 170 + bw + 14, yy + 22, fmt(v), size, colour, "start", 600)
    return s


# ------------------------------------------------------------------ feed
def feed_01():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += crossing(150, 560, 760, 440)
    emit("feed", 1, "sorting-pays-from-the-10th-lookup",
         ["Sorting pays for itself", f"by the {FIRST}th lookup."],
         [f"16 keys: sorting costs at most {WORST} comparisons, then", f"every lookup costs {BIN} instead of {SCAN}."],
         v,
         ["Counted in comparisons. A million keys", f"take about {round(BIG['q_hits'])} lookups to repay it."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    floor = d.SORT["information_floor"]
    rows = [("information floor", floor, f"ceil(log2 16!), cannot be reached", SOFT),
            ("least possible", d.BEST_SORT_16, "worst case, proved in 2023; merge insertion", ACCENT),
            ("merge sort, mean", MEAN, "over all 16! orders", MUTED),
            ("merge sort, worst", WORST, "the cautious break-even uses this", INK)]
    X = lambda c: 120 + (c - 40) / 12 * 820
    v += line(X(40), 980, X(52), 980, MUTED, 1.5)
    for c in range(40, 53, 2):
        v += line(X(c), 974, X(c), 986, MUTED, 1.5) + mono(X(c), 1016, str(c), 18, SOFT, "middle")
    y = 560
    for name, c, note, col in rows:
        v += mono(120, y, name, 21, col, "start", 600)
        v += mono(120, y + 30, note, 18, SOFT)
        v += mono(940, y, fv(c, 2), 24, col, "end", 600)
        v += dot(X(c), 980, 7, col)
        y += 94
    emit("feed", 2, "the-floor-is-45-the-best-is-46",
         ["No sort of 16 keys can", f"promise fewer than {d.BEST_SORT_16}."],
         [f"In the worst case the information floor says {floor}.", f"A computer proof from 2023 says {floor} is not enough."],
         v,
         ["The break-even barely moves:", f"at {d.BEST_SORT_16} the sort is ahead by lookup 9."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    rows = [r_ for r_ in d.SCALE_ROWS if r_["n"] in (16, 256, 4096, 65536, 1 << 20)]
    v += mono(120, 560, "keys n", 20, SOFT, "start", 600)
    v += mono(600, 560, "lookups to repay the sort", 20, SOFT, "start", 600)
    y = 630
    for r_ in rows:
        v += mono(120, y, f"{r_['n']:,}", 26, INK, "start", 500)
        bw = 290 * r_["q_hits"] / 40
        v += rect(600, y - 24, bw, 30, ACCENT)
        v += mono(600 + bw + 14, y, fv(r_["q_hits"], 2), 24, ACCENT, "start", 600)
        y += 92
    emit("feed", 3, "the-break-even-grows-like-log-n",
         ["A million keys repay the", f"sort in about {round(BIG['q_hits'])} lookups."],
         ["Lookups that repay a worst-case merge sort,", "exact at every power of two."],
         v,
         ["The sort costs about log2 n scans,", "and each lookup saves half a scan."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    after = d.KEYS[:I50["slot"]] + [50] + d.KEYS[I50["slot"]:]
    v += mono(110, 556, f"sorted array: {I50['comparisons']} comparisons, then {I50['shifts']} shifts", 21, INK, "start", 600)
    v += array_strip(110, 580, 50, 52, after, moved=I50["shifted"], new=50, size=17)
    v += mono(110, 718, f"TreeMap: {T50['comparisons']} comparisons, {T50['rotations']} rotations, "
                        f"{T50['shifts']} shifts", 21, INK, "start", 600)
    v += mini_tree(118, 774, 52, 58)
    emit("feed", 4, "insert-50",
         ["Insert 50: eight shifts,", "or one path."],
         ["The array moves every key after the slot.", "The red-black tree adds one red leaf."],
         v,
         ["A sorted array loses to plain appending", "once writes reach about half the work."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "writes per read at break-even, against appending", 20, SOFT, "start", 600)
    y = 610
    for n in (16, 1024, 65536):
        v += mono(110, y + 22, f"{n:,} keys", 22, INK, "start", 600)
        v += mono(400, y + 22, "array", 20, MUTED)
        v += mono(560, y + 22, fv(ARR[n], 2), 22, MUTED, "start", 600)
        v += mono(400, y + 62, "tree", 20, ACCENT)
        v += mono(560, y + 62, fv(TREE[n], 1), 22, ACCENT, "start", 600)
        y += 150
    v += mono(110, 1086, "a write = a shift, a store, a rotation or a flip,", 18, SOFT)
    v += mono(110, 1110, "priced like one comparison; lookups hit", 18, SOFT)
    emit("feed", 5, "the-tree-absorbs-writes",
         ["The tree absorbs", f"{about(TREE[65536])} writes per read."],
         ["At 65,536 keys, before plain appending wins.", f"The sorted array absorbs {fv(ARR[65536], 0)}."],
         v,
         ["It pays in memory instead: five references", "and a colour bit in every entry."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    oq = d.OQ
    hit = d.LOOK["binary_hit_counts"]["61"]          # JSON keys are strings
    rows = [("is 61 there?", [f"{hit} comparisons"], [f"{d.SPREAD['lookup_61_eq_calls']} comparison, after", "hashing the key"]),
            ("every key from 40 to 70", [f"{oq['range_comparisons_sorted']} comparisons,", f"then read {oq['range_reads']}"],
             [f"look at all {oq['range_scan_visits']} keys"]),
            ("largest key ≤ 60", [f"{oq['floor_comparisons_sorted']} comparisons: {oq['floor']}"],
             ["integers only:", f"probe 60 down to {oq['floor']}"]),
            ("keys in order", ["read the array"], ["sort them first"])]
    v += mono(110, 556, "query", 19, SOFT, "start", 600)
    v += mono(440, 556, "sorted array", 19, ACCENT, "start", 600)
    v += mono(720, 556, "hash map", 19, LINK, "start", 600)
    y = 630
    for q_, a, h in rows:
        v += hline(110, 970, y - 40, RULE)
        v += txt(110, y, q_, 21, INK, SANS, 600)
        v += "".join(mono(440, y + i * 28, t, 18, ACCENT) for i, t in enumerate(a))
        v += "".join(mono(720, y + i * 28, t, 18, LINK) for i, t in enumerate(h))
        y += 118
    emit("feed", 6, "what-a-hash-map-cannot-answer",
         ["What a hash map", "cannot answer."],
         ["It finds an exact key at once.", "Anything about order, it has to scan for."],
         v,
         ["If any query needs order, keep order:", "an array for reads, a tree for writes."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "key comparisons per insert, all 16 keys sharing one hash", 20, SOFT, "start", 600)
    bw, base = 46, 1020
    for i, c in enumerate(COLL):
        h = 22 * c
        v += rect(130 + i * 52, base - h, bw, h, ACCENT if d.COLL["extra_vs_model"][i] else blend((45, 49, 66), 0.75))
        v += mono(130 + i * 52 + bw / 2, base - h - 12, str(c), 17, INK, "middle", 500)
    v += line(120, base, 960, base, MUTED, 1.5)
    v += mono(130, base + 40, f"total {sum(COLL)}; one list would be {sum(d.COLL['one_list_model'])}; "
                              f"ordinary hashes: {d.SPREAD['insert_total']}", 20, INK, "start", 600)
    v += rect(130, base + 64, 18, 18, ACCENT)
    v += mono(158, base + 79, "compared the first key twice: the probe sequence revisits it", 17, MUTED)
    emit("feed", 7, "sixteen-collisions",
         [f"{len(COLL)} colliding keys,", f"{sum(COLL)} comparisons."],
         ["Every new key is compared with every key", "before it. CPython's dict, counted."],
         v,
         ["Keyed hashes (Python's str) and tree bins", "(Java 8+) are the two fixes."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("sort", f"repaid by lookup {FIRST} at 16 keys", f"after about {round(BIG['q_hits'])} at a million"),
             ("sorted array", "an insert shifts half the keys", "loses at about one write per read"),
             ("red-black tree", "an insert walks one path", f"about {about(TREE[65536])} writes per read at 65,536"),
             ("hash map", "exact keys only, and keys that spread", f"{sum(COLL)} comparisons for 16 colliding")]
    y = 556
    for head, a, b in items:
        v += txt(110, y, head, 30, ACCENT if head == "sort" else INK, SANS, 600)
        v += mono(110, y + 40, a, 21, INK)
        v += mono(110, y + 72, b, 19, SOFT)
        y += 136
    emit("feed", 8, "read-the-article",
         ["Hash map, sorted array", "or tree?"],
         ["Every number counted, from part 1's 16 keys", "to a million, with the lab to rerun it."],
         v,
         ["The full article: the break-even, the write", "share and the queries a hash refuses."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


# ------------------------------------------------------------------ story
def story_01():
    v = crossing(150, 820, 780, 520, label_size=24)
    emit("story", 1, "repaid-by-the-10th-lookup",
         ["Sorting is repaid", f"by lookup {FIRST}."],
         [f"16 keys: {WORST} comparisons to sort,", f"then {fv(SAVE, 3)} saved per lookup."],
         v,
         ["Counted in comparisons, on", "part 1's own 16 keys."],
         STORY_TOTAL)


def story_02():
    after = d.KEYS[:I50["slot"]] + [50] + d.KEYS[I50["slot"]:]
    v = mono(150, 760, f"sorted array: {I50['shifts']} shifts", 26, INK, "start", 600)
    v += array_strip(150, 790, 46, 60, after[4:], moved=I50["shifted"], new=50, size=19)
    v += mono(150, 960, f"TreeMap: {T50['comparisons']} comparisons, {T50['rotations']} rotations", 26, INK, "start", 600)
    v += mini_tree(132, 1036, 51, 64, r_=19, size=15)
    emit("story", 2, "eight-shifts-or-one-path",
         ["Eight shifts,", "or one path."],
         ["Inserting 50 into a sorted array,", "and into Java's red-black TreeMap."],
         v,
         ["The array loses once writes reach", "about half the work."],
         STORY_TOTAL)


def story_03():
    v = mono(150, 790, "comparisons per insert, one shared hash", 24, SOFT, "start", 600)
    base, bw = 1300, 40
    for i, c in enumerate(COLL):
        h = 26 * c
        v += rect(160 + i * 48, base - h, bw, h, ACCENT if d.COLL["extra_vs_model"][i] else blend((45, 49, 66), 0.75))
    v += line(150, base, 940, base, MUTED, 1.5)
    v += mono(150, base + 56, f"16 inserts, {sum(COLL)} comparisons in CPython's dict", 26, INK, "start", 600)
    v += rect(150, base + 86, 22, 22, ACCENT)
    v += mono(186, base + 105, "compared the first key twice", 22, MUTED)
    emit("story", 3, "sixteen-keys-one-hash",
         [f"{sum(COLL)} comparisons", "for 16 keys."],
         ["When every key shares one hash,", "a hash map is a list again."],
         v,
         ["Fix: a keyed hash, or a tree", "inside the bucket."],
         STORY_TOTAL)


def story_04():
    v = box(72, 790, 936, 640, ACCENT_TINT, ACCENT, 8, 1.5)
    steps = [f"sorting is repaid by lookup {FIRST}",
             "writes favour the tree",
             "order questions need order",
             "colliding keys break hashing"]
    y = 900
    for i, s_ in enumerate(steps):
        v += mono(120, y, f"{i + 1}", 34, ACCENT, "start", 600)
        v += txt(180, y, s_, 32, INK, SANS, 600 if i == 0 else 400)
        y += 132
    emit("story", 4, "read-the-article",
         ["Hash map, sorted", "array or tree?"],
         ["When each one", "pays for itself."],
         v,
         ["The full article is on Canery."],
         STORY_TOTAL, cta="LINK IN THE STICKER ABOVE")


BUILDERS = [feed_01, feed_02, feed_03, feed_04, feed_05, feed_06, feed_07, feed_08,
            story_01, story_02, story_03, story_04]

if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for b in BUILDERS:
        name = b.__name__.replace("_", "-")
        if not wanted or name in wanted:
            b()
