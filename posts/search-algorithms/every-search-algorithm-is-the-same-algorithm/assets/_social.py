#!/usr/bin/env python3
"""Build the editable social-card sources for the search-algorithms article."""

from __future__ import annotations

import html
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "social"
ROOT = HERE.parents[2]

PAPER = "#f5f5f5"
INK = "#2d3142"
MUTED = "#4f5d75"
SOFT = "#7a8399"
RULE = "rgba(45,49,66,0.14)"
SILVER = "#bfc0c0"
ACCENT = "#eb6c36"
ACCENT_TINT = "rgba(235,108,54,0.08)"
WHITE = "#ffffff"
SERIF = "'Instrument Serif', Georgia, serif"
SANS = "'Geist', system-ui, sans-serif"
MONO = "'Geist Mono', ui-monospace, monospace"
FONTS = (
    "https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
    "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap"
)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def text(x, y, value, *, size=20, fill=INK, family=SANS, weight="400", anchor="start", track=None):
    tracking = f' letter-spacing="{track}"' if track else ""
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
        f'font-weight="{weight}" font-family="{family}" text-anchor="{anchor}"{tracking}>'
        f'{esc(value)}</text>'
    )


def lines(x, y, values, *, size=20, fill=INK, family=SANS, weight="400", gap=None, anchor="start"):
    gap = gap or int(size * 1.25)
    return "".join(
        text(x, y + index * gap, value, size=size, fill=fill, family=family,
             weight=weight, anchor=anchor)
        for index, value in enumerate(values)
    )


def mono(x, y, value, *, size=15, fill=MUTED, weight="400", anchor="start", track=None):
    return text(x, y, value, size=size, fill=fill, family=MONO, weight=weight,
                anchor=anchor, track=track)


def label(x, y, value, *, fill=SOFT, anchor="start", size=13):
    return mono(x, y, str(value).upper(), size=size, fill=fill, weight="500",
                anchor=anchor, track="0.12em")


def box(x, y, width, height, *, fill=WHITE, stroke=RULE, radius=8, sw=1):
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
    )


def rule(x1, y1, x2, y2, *, stroke=RULE, width=1, marker=False):
    end = ' marker-end="url(#arrow)"' if marker else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{width}"{end}/>'


def logo_paths() -> str:
    source = (ROOT / "web/public/brand/canerly-lockup-horizontal.svg").read_text(encoding="utf-8")
    paths = re.findall(r"<path\b[\s\S]*?/>", source)
    if len(paths) != 2:
        raise RuntimeError("Could not read the canonical Canery horizontal lockup")
    return "\n".join(paths)


LOGO_PATHS = logo_paths()

DEFS = f"""
<defs>
  <style>@import url('{FONTS}');</style>
  <marker id="arrow" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">
    <polygon points="0 0, 9 3.5, 0 7" fill="{MUTED}"/>
  </marker>
</defs>
"""


def shell(kind, number, total, title_lines, deck_lines, visual, takeaway_lines, *, footer=None):
    if kind == "feed":
        width, height = 1080, 1350
        logo_y, logo_width, logo_scale = 72, 180, 0.2680965
        rule_y, title_y, title_size, title_gap = 150, 238, 58, 65
        deck_size, deck_gap = 22, 30
        takeaway_rule, takeaway_y, footer_y = 1168, 1220, 1305
    else:
        width, height = 1080, 1920
        logo_y, logo_width, logo_scale = 250, 200, 0.297885
        rule_y, title_y, title_size, title_gap = 340, 466, 70, 80
        deck_size, deck_gap = 26, 36
        takeaway_rule, takeaway_y, footer_y = 1505, 1570, 1665

    deck_y = title_y + len(title_lines) * title_gap + 22
    logo = (
        f'<g data-canery-logo="lockup" data-logo-x="72" data-logo-y="{logo_y}" '
        f'data-logo-width="{logo_width}" fill="{INK}" '
        f'transform="translate(72 {logo_y}) scale({logo_scale})">{LOGO_PATHS}</g>'
    )
    body = f'<rect width="{width}" height="{height}" fill="{PAPER}"/>'
    body += logo
    body += label(1008, logo_y + 35, f"{number:02d} / {total:02d}", anchor="end", size=15)
    body += rule(72, rule_y, 1008, rule_y)
    body += lines(72, title_y, title_lines, size=title_size, family=SERIF, gap=title_gap)
    body += lines(72, deck_y, deck_lines, size=deck_size, fill=MUTED, gap=deck_gap)
    body += visual
    body += rule(72, takeaway_rule, 1008, takeaway_rule)
    body += lines(72, takeaway_y, takeaway_lines,
                  size=22 if kind == "feed" else 27, weight="600",
                  gap=30 if kind == "feed" else 36)
    body += label(72, footer_y, footer or "THE PRICE OF THE SKIP · CANERY",
                  fill=ACCENT if footer else SOFT, size=14 if kind == "feed" else 16)
    description = esc(" ".join(title_lines + deck_lines + takeaway_lines))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img">'
        f'<title>{esc(" ".join(title_lines))}</title><desc>{description}</desc>'
        f'{DEFS}{body}</svg>'
    )


def emit(kind, number, slug, title_lines, deck_lines, visual, takeaway_lines, *, total, footer=None):
    svg = shell(kind, number, total, title_lines, deck_lines, visual, takeaway_lines, footer=footer)
    document = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f'<title>{esc(" ".join(title_lines))}</title><link href="{FONTS}" rel="stylesheet">'
        f'<style>html,body{{margin:0;background:{PAPER}}}svg{{display:block}}</style>'
        f'</head><body>{svg}</body></html>'
    )
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{kind}-{number:02d}-{slug}.html"
    path.write_text(document, encoding="utf-8")
    print(path.name)


def stat_card(x, y, width, tag, main, detail, *, focal=False):
    result = box(x, y, width, 128, fill=ACCENT_TINT if focal else WHITE,
                 stroke=ACCENT if focal else RULE, sw=1.2 if focal else 1)
    result += label(x + 20, y + 28, tag, fill=ACCENT if focal else SOFT, size=12)
    result += text(x + 20, y + 64, main, size=23, weight="600",
                   fill=ACCENT if focal else INK)
    result += mono(x + 20, y + 98, detail, size=14, fill=MUTED)
    return result


def feed_01():
    visual = ""
    xs = [72, 312, 552, 792]
    names = [("FRONTIER", "candidates"), ("PROBE", "one choice"),
             ("ELIMINATE", "ruled out"), ("REPEAT", "smaller set")]
    for index, ((name, detail), x) in enumerate(zip(names, xs)):
        focal = name == "ELIMINATE"
        visual += box(x, 500, 216, 132, fill=ACCENT_TINT if focal else WHITE,
                      stroke=ACCENT if focal else RULE)
        visual += label(x + 20, 534, name, fill=ACCENT if focal else SOFT, size=12)
        visual += text(x + 20, 584, detail, size=21, weight="600")
        if index < 3:
            visual += rule(x + 216, 566, x + 234, 566, marker=True)
    visual += box(72, 680, 936, 196, fill=INK, stroke=INK, radius=8)
    visual += mono(104, 724, "while frontier:", size=17, fill=WHITE, weight="600")
    visual += mono(134, 762, "candidate = pick(frontier)", size=16, fill="#d9dbe3")
    visual += mono(134, 798, "result = test(candidate)", size=16, fill="#d9dbe3")
    visual += mono(134, 834, "frontier = eliminate(frontier, candidate, result)", size=16,
                   fill="#ffad84", weight="600")
    chips = [("BINARY", "sorted order"), ("KMP", "overlap table"),
             ("A*", "heuristic"), ("HNSW", "proximity graph")]
    for index, (name, detail) in enumerate(chips):
        x = 72 + index * 240
        visual += box(x, 922, 216, 112, fill=WHITE, stroke=RULE)
        visual += label(x + 18, 954, name, size=12)
        visual += mono(x + 18, 998, detail, size=14, fill=MUTED)
    emit("feed", 1, "one-loop-different-skip",
         ["Every search algorithm", "runs the same loop."],
         ["Binary search, KMP, A*, and HNSW change one box:", "how the probe eliminates candidates."],
         visual,
         ["The loop is ordinary. The prepaid elimination rule", "is the algorithm."], total=6)


def feed_02():
    visual = ""
    values = [3, 9, 14, 21, 28, 35, 42, 47, 53, 61, 68, 74, 79, 85, 91, 97]
    cell_w = 58
    for index, value in enumerate(values):
        x = 72 + index * cell_w
        fill = ACCENT_TINT if index == 9 else WHITE
        stroke = ACCENT if index == 9 else RULE
        visual += box(x, 485, 54, 68, fill=fill, stroke=stroke, radius=5)
        visual += mono(x + 27, 526, value, size=14, fill=ACCENT if index == 9 else INK,
                       weight="600", anchor="middle")
        visual += mono(x + 27, 574, index, size=11, fill=SOFT, anchor="middle")
    cards = [
        ("PROBE 1", "a[7] = 47", "eliminate indices 0–7", "8 gone"),
        ("PROBE 2", "a[11] = 74", "eliminate indices 11–15", "5 gone"),
        ("PROBE 3", "a[9] = 61", "target found", "FOUND"),
    ]
    for index, (tag, main, detail, result) in enumerate(cards):
        x = 72 + index * 320
        focal = index == 2
        visual += box(x, 640, 296, 210, fill=ACCENT_TINT if focal else WHITE,
                      stroke=ACCENT if focal else RULE)
        visual += label(x + 22, 674, tag, fill=ACCENT if focal else SOFT, size=12)
        visual += text(x + 22, 720, main, size=23, weight="600")
        visual += mono(x + 22, 760, detail, size=14, fill=MUTED)
        visual += text(x + 22, 816, result, size=20, weight="600",
                       fill=ACCENT if focal else INK)
    visual += box(72, 900, 936, 96, fill=INK, stroke=INK, radius=8)
    visual += mono(540, 958, "16  →  8  →  3  →  FOUND", size=22, fill=WHITE,
                   weight="600", anchor="middle")
    visual += label(540, 1055, "linear scan: 10 probes · ordered search: 3 probes",
                    fill=ACCENT, anchor="middle", size=14)
    emit("feed", 2, "three-probes-vs-ten",
         ["Same target.", "Three probes vs ten."],
         ["Search for 61 in the article’s 16 sorted integers.", "Order changes eliminations—not comparison speed."],
         visual,
         ["The probes buy 8, then 5, then 2 eliminations.", "Sorted order raises the exchange rate."], total=6)


def feed_03():
    visual = ""
    cards = [
        ("01 · ORDERING", "Binary search", ["wrong half is impossible", "exact · ≈ log₂ n probes"]),
        ("02 · PRECOMPUTATION", "KMP", ["LPS table preserves matches", "exact · O(m + n)"]),
        ("03 · HEURISTIC", "A*", ["f(v) = g(v) + h(v)", "exact with admissible h"]),
        ("04 · GEOMETRY", "HNSW", ["coarse-to-fine graph walk", "approximate · tune recall"]),
    ]
    for index, (tag, title, detail) in enumerate(cards):
        col, row = index % 2, index // 2
        x, y = 72 + col * 480, 485 + row * 250
        focal = index == 3
        visual += box(x, y, 456, 220, fill=ACCENT_TINT if focal else WHITE,
                      stroke=ACCENT if focal else RULE)
        visual += label(x + 24, y + 36, tag, fill=ACCENT if focal else SOFT, size=12)
        visual += text(x + 24, y + 84, title, size=27, weight="600")
        visual += lines(x + 24, y + 130, detail, size=15, family=MONO, fill=MUTED, gap=29)
    visual += box(72, 1010, 936, 68, fill=INK, stroke=INK, radius=7)
    visual += mono(540, 1052, "BUILD · MAINTAIN · LAY OUT · OR TRADE ACCURACY", size=16,
                   fill=WHITE, weight="600", anchor="middle")
    emit("feed", 3, "four-ways-to-buy-the-skip",
         ["Four structures", "buy the skip."],
         ["Each lets one probe say something about candidates", "that were never tested directly."],
         visual,
         ["Faster queries are never free. The price moves into", "build time, maintenance, memory, or recall."], total=6)


def feed_04():
    visual = ""
    visual += box(72, 500, 936, 230, fill=WHITE, stroke=RULE)
    visual += label(96, 538, "mismatch after five matches", size=12)
    visual += mono(96, 590, "TEXT     A A B A A B A A B A A C", size=18, fill=INK, weight="600")
    visual += mono(96, 636, "PATTERN  A A B A A C", size=18, fill=MUTED)
    visual += mono(96, 682, "                    ↑ text[5]=B · pattern[5]=C", size=15,
                   fill=ACCENT, weight="600")
    visual += stat_card(72, 775, 456, "naive shift", "rewind the text", "shift 1 · text pointer → 1")
    visual += stat_card(552, 775, 456, "KMP shift", "keep i at 5", "lps[4] = 2 · pattern j → 2", focal=True)
    visual += rule(280, 956, 800, 956, stroke=MUTED, width=2, marker=True)
    visual += mono(280, 994, "text positions visited: 0 · 1 · 2 · … · 11", size=16,
                   fill=MUTED)
    visual += label(540, 1046, "text pointer never moves backward", fill=ACCENT,
                    anchor="middle", size=13)
    emit("feed", 4, "kmp-never-rewinds-text",
         ["KMP keeps the text", "pointer moving forward."],
         ["Pattern AABAAC mismatches after AABAA against", "text AABAABAABAAC. The overlap table saves work."],
         visual,
         ["The LPS table remembers the verified suffix.", "That buys O(m + n) worst-case matching."], total=6)


def feed_05():
    visual = ""
    visual += box(72, 500, 456, 300, fill=WHITE, stroke=RULE)
    visual += label(96, 536, "Dijkstra", size=12)
    visual += text(96, 586, "f(v) = g(v) + 0", size=28, family=MONO, weight="600")
    visual += text(96, 640, "58 cells expanded", size=22, weight="600")
    visual += mono(96, 680, "broad frontier from the start", size=15, fill=MUTED)
    for col in range(7):
        fill = "#d9dbe3" if col < 6 else PAPER
        visual += box(96 + col * 42, 710, 30, 30, fill=fill, stroke=RULE, radius=3)
    visual += box(552, 500, 456, 300, fill=ACCENT_TINT, stroke=ACCENT)
    visual += label(576, 536, "A*", fill=ACCENT, size=12)
    visual += text(576, 586, "f(v) = g(v) + h(v)", size=28, family=MONO, weight="600")
    visual += text(576, 640, "33 cells expanded", size=22, weight="600")
    visual += mono(576, 680, "heuristic biases toward the goal", size=15, fill=MUTED)
    visual += rule(600, 744, 938, 744, stroke=ACCENT, width=5, marker=True)
    visual += label(600, 780, "same grid · same cost-11 path", fill=ACCENT, size=12)
    visual += stat_card(72, 850, 456, "result guarantee", "admissible", "h(v) ≤ h*(v) · least-cost path")
    visual += stat_card(552, 850, 456, "expansion claim", "consistent", "h(u) ≤ c(u,v) + h(v)", focal=True)
    emit("feed", 5, "dijkstra-is-a-star-zero",
         ["Dijkstra is A*", "with the knob at zero."],
         ["The article’s grid keeps the same cost-11 path.", "A heuristic changes which frontier nodes get probed."],
         visual,
         ["Set h(v)=0 and A* becomes Dijkstra exactly.", "Do not quote stronger guarantees without conditions."], total=6)


def feed_06():
    visual = ""
    visual += label(72, 490, "PREPAID STRUCTURE", size=12)
    visual += label(410, 490, "THE SKIP", size=12)
    visual += label(720, 490, "WHAT TO WATCH", size=12)
    rows = [
        ("sorted order", "discard one side", "sort + O(n) inserts"),
        ("LPS table", "reuse matched prefix", "pattern preprocessing"),
        ("heuristic h", "bias the frontier", "admissible / consistent"),
        ("proximity graph", "probable elimination", "recall ↔ throughput"),
    ]
    for index, (structure, skip, watch) in enumerate(rows):
        y = 515 + index * 112
        focal = index == 3
        visual += box(72, y, 936, 92, fill=ACCENT_TINT if focal else WHITE,
                      stroke=ACCENT if focal else RULE, radius=6)
        visual += text(96, y + 55, structure, size=20, weight="600")
        visual += mono(410, y + 55, skip, size=15, fill=MUTED)
        visual += mono(720, y + 55, watch, size=15, fill=ACCENT if focal else MUTED)
    visual += box(72, 990, 936, 92, fill=INK, stroke=INK, radius=8)
    visual += label(96, 1022, "decision check", fill="#ffad84", size=12)
    visual += mono(96, 1055, "build · queries/rebuild · writes · memory · accuracy", size=17,
                   fill=WHITE, weight="600")
    emit("feed", 6, "the-skip-has-a-price",
         ["The skip always", "has a price."],
         ["Query complexity hides where the useful structure", "was built and what keeps it valid."],
         visual,
         ["Before choosing a search structure, ask how many", "queries will repay its build and maintenance cost."],
         total=6, footer="READ THE FULL GUIDE · CANERY.IN/BLOGS/EVERY-SEARCH-ALGORITHM-IS-THE-SAME-ALGORITHM")


def story_01():
    visual = ""
    stages = [("FRONTIER", "hold candidates"), ("PROBE", "test one"),
              ("ELIMINATE", "remove many"), ("REPEAT", "smaller frontier")]
    for index, (name, detail) in enumerate(stages):
        x = 72 + (index % 2) * 480
        y = 760 + (index // 2) * 180
        focal = name == "ELIMINATE"
        visual += box(x, y, 456, 145, fill=ACCENT_TINT if focal else WHITE,
                      stroke=ACCENT if focal else RULE)
        visual += label(x + 24, y + 38, name, fill=ACCENT if focal else SOFT, size=12)
        visual += text(x + 24, y + 91, detail, size=26, weight="600")
    visual += box(72, 1155, 936, 130, fill=INK, stroke=INK)
    visual += mono(96, 1204, "binary · KMP · A* · HNSW", size=20, fill=WHITE, weight="600")
    visual += mono(96, 1248, "same loop · different prepaid elimination rule", size=16,
                   fill="#ffad84")
    emit("story", 1, "same-loop-different-rule",
         ["Every search algorithm", "runs the same loop."],
         ["What changes is how one probe can", "eliminate candidates it never tested."],
         visual,
         ["The eliminate step is", "where the algorithm lives."], total=4)


def story_02():
    visual = ""
    values = [3, 9, 14, 21, 28, 35, 42, 47, 53, 61, 68, 74, 79, 85, 91, 97]
    for index, value in enumerate(values):
        x = 72 + index * 58
        visual += box(x, 745, 54, 64, fill=ACCENT_TINT if index == 9 else WHITE,
                      stroke=ACCENT if index == 9 else RULE, radius=4)
        visual += mono(x + 27, 785, value, size=13, fill=ACCENT if index == 9 else INK,
                       weight="600", anchor="middle")
    steps = [
        ("1", "a[7] = 47", "16 → 8", "eliminate 0–7"),
        ("2", "a[11] = 74", "8 → 3", "eliminate 11–15"),
        ("3", "a[9] = 61", "FOUND", "target at index 9"),
    ]
    for index, (number, probe, result, detail) in enumerate(steps):
        y = 855 + index * 170
        focal = index == 2
        visual += box(72, y, 936, 140, fill=ACCENT_TINT if focal else WHITE,
                      stroke=ACCENT if focal else RULE)
        visual += mono(100, y + 56, number, size=24, fill=ACCENT if focal else SOFT,
                       weight="600")
        visual += text(160, y + 55, probe, size=24, weight="600")
        visual += mono(160, y + 98, detail, size=15, fill=MUTED)
        visual += text(960, y + 72, result, size=25, weight="600",
                       fill=ACCENT if focal else INK, anchor="end")
    emit("story", 2, "binary-search-three-probes",
         ["Order turns ten probes", "into three."],
         ["Target 61 in the same 16-value array.", "Only the elimination rate changes."],
         visual,
         ["16 → 8 → 3 → found.", "One comparison rules out a region."], total=4)


def story_03():
    visual = ""
    items = [
        ("ORDER", "Binary search", "wrong half is impossible", "exact"),
        ("TABLE", "KMP", "text pointer never rewinds", "O(m+n)"),
        ("HEURISTIC", "A*", "f = g + h guides frontier", "admissible"),
        ("GEOMETRY", "HNSW", "coarse-to-fine graph", "approx"),
    ]
    for index, (tag, name, detail, result) in enumerate(items):
        y = 735 + index * 176
        focal = index == 3
        visual += box(72, y, 936, 148, fill=ACCENT_TINT if focal else WHITE,
                      stroke=ACCENT if focal else RULE)
        visual += label(100, y + 38, tag, fill=ACCENT if focal else SOFT, size=12)
        visual += text(100, y + 89, name, size=26, weight="600")
        visual += mono(380, y + 86, detail, size=15, fill=MUTED)
        visual += label(970, y + 84, result, fill=ACCENT if focal else INK,
                        anchor="end", size=13)
    emit("story", 3, "four-prices-for-the-skip",
         ["Four ways to", "buy the skip."],
         ["Each structure links one probe", "to candidates it never touches."],
         visual,
         ["Prepay with build, maintenance,", "memory—or accuracy."], total=4)


def story_04():
    visual = ""
    visual += box(72, 740, 936, 230, fill=ACCENT_TINT, stroke=ACCENT)
    visual += label(100, 785, "the decision the article teaches", fill=ACCENT, size=12)
    visual += lines(100, 844, ["What relation lets one probe", "eliminate many candidates?"],
                    size=30, weight="600", gap=40)
    checks = ["BUILD COST", "QUERIES / REBUILD", "WRITES", "MEMORY", "ACCURACY"]
    for index, item in enumerate(checks):
        col, row = index % 2, index // 2
        x, y = 72 + col * 480, 1030 + row * 105
        width = 456 if index < 4 else 936
        visual += box(x if index < 4 else 72, y, width, 78, fill=WHITE, stroke=RULE)
        visual += label((x if index < 4 else 72) + 24, y + 48, item, size=13,
                        fill=ACCENT if index == 4 else INK)
    visual += box(170, 1350, 740, 100, fill=INK, stroke=INK, radius=10)
    visual += text(540, 1393, "Read the full article on Canery", size=25, fill=WHITE,
                   weight="600", anchor="middle")
    visual += mono(540, 1426, "use the link sticker below", size=15, fill=SILVER,
                   anchor="middle")
    emit("story", 4, "read-the-search-guide",
         ["Ask what the skip", "cost before using it."],
         ["Fast queries are a prepaid asset—not", "a property of the loop itself."],
         visual,
         ["Compare the whole workload,", "not one asymptotic bound."], total=4,
         footer="LINK STICKER · READ THE ARTICLE")


BUILDERS = [feed_01, feed_02, feed_03, feed_04, feed_05, feed_06,
            story_01, story_02, story_03, story_04]


if __name__ == "__main__":
    requested = set(sys.argv[1:])
    for builder in BUILDERS:
        name = builder.__name__.replace("_", "-")
        if not requested or name in requested:
            builder()
