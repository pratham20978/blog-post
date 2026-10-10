#!/usr/bin/env python3
"""Build the finished Blog Forge social HTML sources for this article.

The feed sequence promotes the article's existing measured LinkedIn frames into
the shared Instagram/LinkedIn contract and adds the locked Canery lockup. Story
frames are independently composed for 9:16. SVG and PNG exports are produced by
the plugin's deterministic render_social.py script.
"""

from __future__ import annotations

import html
import pathlib
import re


ASSETS = pathlib.Path(__file__).resolve().parent
WORKSPACE = pathlib.Path(__file__).resolve().parents[3]
PLUGIN_ASSETS = (
    WORKSPACE / ".claude" / "blog-forge" / "skills" / "blog-visuals" / "assets"
)
SOCIAL = ASSETS / "social"

FONT_LINK = (
    "https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&"
    "family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap"
)

FEED_SOURCES = (
    (
        "linkedin-01-one-parent.html",
        "feed-01-one-parent",
        "POSTGRESQL FOUNDATIONS · PART 2",
        "PostgreSQL is not one program",
        "A process tree showing the postmaster above client and background processes.",
    ),
    (
        "linkedin-02-five-passes.html",
        "feed-02-five-index-passes",
        "VACUUM MEMORY",
        "The same delete needs five index passes or one",
        "Measured vacuum passes at one and 256 megabytes of maintenance work memory.",
    ),
    (
        "linkedin-03-thirty-seconds.html",
        "feed-03-thirty-seconds",
        "AUTOVACUUM CLOCK",
        "Thirty seconds waiting, thirty milliseconds working",
        "A measured autovacuum arrival timeline for the customers table.",
    ),
    (
        "linkedin-04-one-budget.html",
        "feed-04-one-shared-budget",
        "AUTOVACUUM BUDGET",
        "More workers share the same cost budget",
        "One, three, and eight workers divide one 200-unit autovacuum budget.",
    ),
    (
        "linkedin-05-sixteen-times.html",
        "feed-05-sixteen-times",
        "WAL COMMIT PATH",
        "Synchronous commit changes what the backend waits for",
        "Measured throughput and fdatasync calls with synchronous commit on and off.",
    ),
    (
        "linkedin-06-one-killed-backend.html",
        "feed-06-one-killed-backend",
        "CRASH RECOVERY · READ THE ARTICLE",
        "One killed backend resets every server process",
        "The PostgreSQL log sequence after one backend is killed with signal nine.",
    ),
)


def template_parts(kind: str) -> tuple[str, str]:
    template = (PLUGIN_ASSETS / f"social-{kind}-template.html").read_text(encoding="utf-8")
    definition = re.search(
        rf'<g id="canery-lockup-{kind}"[\s\S]*?</g>', template
    )
    marker = re.search(
        r'<g data-canery-logo="lockup"[^>]*>[\s\S]*?</g>', template
    )
    if definition is None or marker is None:
        raise RuntimeError(f"locked {kind} template is missing the Canery lockup")
    return definition.group(0), marker.group(0)


def wrap_html(title: str, svg: str) -> str:
    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        f"<title>{html.escape(title)}</title><link href=\"{FONT_LINK}\" rel=\"stylesheet\">"
        "<style>html,body{margin:0;background:#f5f5f5}svg{display:block}</style>"
        f"</head><body>{svg}</body></html>\n"
    )


def add_svg_accessibility(svg: str, title: str, description: str) -> str:
    opening = re.search(r"<svg\b[^>]*>", svg)
    if opening is None:
        raise RuntimeError("source has no SVG opening tag")
    accessible = (
        opening.group(0)
        + f"<title>{html.escape(title)}</title>"
        + f"<desc>{html.escape(description)}</desc>"
    )
    return svg[: opening.start()] + accessible + svg[opening.end() :]


def build_feed() -> None:
    lockup_definition, lockup_marker = template_parts("feed")
    for index, (source_name, stem, label, title, description) in enumerate(
        FEED_SOURCES, 1
    ):
        source = (ASSETS / source_name).read_text(encoding="utf-8")
        match = re.search(r"<svg\b[^>]*>[\s\S]*?</svg>", source)
        if match is None:
            raise RuntimeError(f"{source_name} has no inline SVG")
        svg = match.group(0)
        svg = svg.replace("</defs>", lockup_definition + "</defs>", 1)
        background = '<rect width="100%" height="100%" fill="#f5f5f5"/>'
        if background not in svg:
            raise RuntimeError(f"{source_name} has no expected background")
        svg = svg.replace(background, background + lockup_marker, 1)
        header = (
            '<text x="300" y="107" fill="#7a8399" font-size="14" '
            'font-weight="500" font-family="\'Geist Mono\', ui-monospace, monospace" '
            f'text-anchor="start" letter-spacing="0.12em">{label}</text>'
        )
        counter_fill = "#eb6c36" if index == len(FEED_SOURCES) else "#7a8399"
        counter = (
            f'<text x="1008" y="107" fill="{counter_fill}" font-size="15" '
            'font-weight="500" font-family="\'Geist Mono\', ui-monospace, monospace" '
            f'text-anchor="end" letter-spacing="0.12em">{index:02d} / 06</text>'
        )
        svg, first = re.subn(
            r'<text x="80" y="120"[^>]*>.*?</text>', header, svg, count=1
        )
        svg, second = re.subn(
            r'<text x="1000" y="120"[^>]*>.*?</text>', counter, svg, count=1
        )
        if first != 1 or second != 1:
            raise RuntimeError(f"{source_name} does not match the feed header contract")
        svg = svg.replace(
            '<line x1="80" y1="148" x2="1000" y2="148"',
            '<line x1="72" y1="150" x2="1008" y2="150"',
            1,
        )
        svg = add_svg_accessibility(svg, title, description)
        (SOCIAL / f"{stem}.html").write_text(
            wrap_html(title, svg), encoding="utf-8"
        )


def story_shell(index: int, title: str, description: str, content: str) -> str:
    definition, marker = template_parts("story")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" width="1080" height="1920" role="img">
  <title>{html.escape(title)}</title>
  <desc>{html.escape(description)}</desc>
  <defs>{definition}</defs>
  <rect width="1080" height="1920" fill="#f5f5f5"/>
  {marker}
  <text x="1008" y="285" fill="#7a8399" font-size="17" font-weight="500" font-family="'Geist Mono', ui-monospace, monospace" text-anchor="end" letter-spacing="0.12em">{index:02d} / 04</text>
  <line x1="72" y1="340" x2="1008" y2="340" stroke="rgba(45,49,66,0.12)"/>
  {content}
</svg>'''
    return wrap_html(title, svg)


def build_stories() -> None:
    stories = {
        "story-01-one-supervisor": story_shell(
            1,
            "PostgreSQL is one supervisor and many processes",
            "The postmaster sits above five permanent background processes and client backends.",
            '''<text x="72" y="470" fill="#2d3142" font-size="72" font-family="'Instrument Serif', Georgia, serif">PostgreSQL is not</text>
  <text x="72" y="550" fill="#2d3142" font-size="72" font-family="'Instrument Serif', Georgia, serif">one program.</text>
  <text x="72" y="650" fill="#4f5d75" font-size="26" font-family="'Geist', system-ui, sans-serif">One supervisor forks every client and background process.</text>
  <text x="72" y="686" fill="#4f5d75" font-size="26" font-family="'Geist', system-ui, sans-serif">The supervisor itself never runs a query or reads a page.</text>
  <rect x="340" y="780" width="400" height="116" rx="8" fill="rgba(235,108,54,0.08)" stroke="#eb6c36" stroke-width="2"/>
  <text x="540" y="824" fill="#eb6c36" font-size="13" font-weight="600" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing=".12em">ONLY PROCESS ALLOWED TO FORK</text>
  <text x="540" y="862" fill="#2d3142" font-size="25" font-weight="600" font-family="'Geist', sans-serif" text-anchor="middle">postmaster</text>
  <line x1="540" y1="896" x2="180" y2="1020" stroke="rgba(45,49,66,.30)"/>
  <line x1="540" y1="896" x2="540" y2="1020" stroke="rgba(45,49,66,.30)"/>
  <line x1="540" y1="896" x2="900" y2="1020" stroke="rgba(45,49,66,.30)"/>
  <line x1="540" y1="896" x2="180" y2="1200" stroke="rgba(45,49,66,.30)"/>
  <line x1="540" y1="896" x2="540" y2="1200" stroke="rgba(45,49,66,.30)"/>
  <line x1="540" y1="896" x2="900" y2="1200" stroke="rgba(45,49,66,.30)"/>
  <g font-family="'Geist Mono', monospace" font-size="15" text-anchor="middle">
    <rect x="72" y="1020" width="216" height="104" rx="7" fill="#fff" stroke="#bfc0c0"/><text x="180" y="1062" fill="#2d3142" font-weight="600">client backend</text><text x="180" y="1092" fill="#4f5d75">one / connection</text>
    <rect x="432" y="1020" width="216" height="104" rx="7" fill="#fff" stroke="#bfc0c0"/><text x="540" y="1062" fill="#2d3142" font-weight="600">checkpointer</text><text x="540" y="1092" fill="#4f5d75">redo boundary</text>
    <rect x="792" y="1020" width="216" height="104" rx="7" fill="#fff" stroke="#bfc0c0"/><text x="900" y="1062" fill="#2d3142" font-weight="600">background writer</text><text x="900" y="1092" fill="#4f5d75">free buffers</text>
    <rect x="72" y="1200" width="216" height="104" rx="7" fill="#fff" stroke="#bfc0c0"/><text x="180" y="1242" fill="#2d3142" font-weight="600">WAL writer</text><text x="180" y="1272" fill="#4f5d75">log flushes</text>
    <rect x="432" y="1200" width="216" height="104" rx="7" fill="#fff" stroke="#bfc0c0"/><text x="540" y="1242" fill="#2d3142" font-weight="600">av launcher</text><text x="540" y="1272" fill="#4f5d75">keeps time</text>
    <rect x="792" y="1200" width="216" height="104" rx="7" fill="#fff" stroke="#bfc0c0"/><text x="900" y="1242" fill="#2d3142" font-weight="600">av worker</text><text x="900" y="1272" fill="#4f5d75">cleans tables</text>
  </g>
  <line x1="72" y1="1510" x2="1008" y2="1510" stroke="rgba(45,49,66,.12)"/>
  <text x="72" y="1575" fill="#2d3142" font-size="28" font-weight="600" font-family="'Geist', sans-serif">Name the process. Then tune the decision it owns.</text>
  <text x="72" y="1655" fill="#7a8399" font-size="16" font-weight="500" font-family="'Geist Mono', monospace" letter-spacing=".12em">POSTGRESQL PROCESS LAYER · CANERY</text>''',
        ),
        "story-02-thirty-seconds": story_shell(
            2,
            "Thirty seconds waiting, thirty milliseconds working",
            "The customers table crosses its vacuum threshold and waits for the launcher.",
            '''<text x="72" y="470" fill="#2d3142" font-size="70" font-family="'Instrument Serif', Georgia, serif">30 seconds waiting.</text>
  <text x="72" y="550" fill="#2d3142" font-size="70" font-family="'Instrument Serif', Georgia, serif">30 ms working.</text>
  <text x="72" y="650" fill="#4f5d75" font-size="26" font-family="'Geist', sans-serif">The table qualified immediately. The launcher was asleep.</text>
  <rect x="72" y="730" width="936" height="220" rx="8" fill="#fff" stroke="#bfc0c0"/>
  <text x="104" y="778" fill="#7a8399" font-size="14" font-weight="600" font-family="'Geist Mono', monospace" letter-spacing=".12em">DEFAULT VACUUM THRESHOLD</text>
  <text x="104" y="832" fill="#2d3142" font-size="24" font-weight="600" font-family="'Geist Mono', monospace">50 + 0.2 × reltuples</text>
  <text x="104" y="888" fill="#4f5d75" font-size="20" font-family="'Geist', sans-serif">customers: 100,000 rows → 20,050 dead tuples</text>
  <text x="104" y="920" fill="#eb6c36" font-size="20" font-weight="600" font-family="'Geist', sans-serif">UPDATE created 30,000 dead tuples → qualified now</text>
  <text x="72" y="1030" fill="#7a8399" font-size="14" font-weight="600" font-family="'Geist Mono', monospace" letter-spacing=".12em">MEASURED TIMELINE · POSTGRESQL 16.2</text>
  <line x1="104" y1="1120" x2="940" y2="1120" stroke="#2d3142" stroke-width="3"/>
  <circle cx="104" cy="1120" r="13" fill="#2d3142"/>
  <circle cx="920" cy="1120" r="15" fill="#eb6c36"/>
  <rect x="104" y="1098" width="816" height="44" fill="rgba(45,49,66,.06)"/>
  <text x="104" y="1180" fill="#2d3142" font-size="18" font-weight="600" font-family="'Geist Mono', monospace">0 s · UPDATE commits</text>
  <text x="920" y="1180" fill="#eb6c36" font-size="18" font-weight="600" font-family="'Geist Mono', monospace" text-anchor="end">30.0 s · worker appears</text>
  <text x="512" y="1082" fill="#4f5d75" font-size="17" font-family="'Geist Mono', monospace" text-anchor="middle">launcher waits for its next database visit</text>
  <rect x="680" y="1260" width="328" height="126" rx="8" fill="rgba(235,108,54,.08)" stroke="#eb6c36"/>
  <text x="844" y="1304" fill="#eb6c36" font-size="14" font-weight="600" font-family="'Geist Mono', monospace" text-anchor="middle">WORKER LOG</text>
  <text x="844" y="1342" fill="#2d3142" font-size="21" font-weight="600" font-family="'Geist', sans-serif" text-anchor="middle">30,000 removed</text>
  <text x="844" y="1372" fill="#4f5d75" font-size="16" font-family="'Geist Mono', monospace" text-anchor="middle">elapsed: 0.03 s</text>
  <line x1="72" y1="1510" x2="1008" y2="1510" stroke="rgba(45,49,66,.12)"/>
  <text x="72" y="1570" fill="#2d3142" font-size="27" font-weight="600" font-family="'Geist', sans-serif">Halving naptime halves the wait—not the work.</text>
  <text x="72" y="1655" fill="#7a8399" font-size="16" font-weight="500" font-family="'Geist Mono', monospace" letter-spacing=".12em">AUTOVACUUM CLOCK · CANERY</text>''',
        ),
        "story-03-five-index-passes": story_shell(
            3,
            "The same delete needs five index passes or one",
            "Vacuuming 800,000 dead tuples at one and 256 megabytes of work memory.",
            '''<text x="72" y="470" fill="#2d3142" font-size="70" font-family="'Instrument Serif', Georgia, serif">Same delete.</text>
  <text x="72" y="550" fill="#2d3142" font-size="70" font-family="'Instrument Serif', Georgia, serif">Five passes or one.</text>
  <text x="72" y="650" fill="#4f5d75" font-size="26" font-family="'Geist', sans-serif">800,000 dead tuples. Two indexes. One memory setting.</text>
  <rect x="72" y="730" width="936" height="286" rx="8" fill="rgba(235,108,54,.08)" stroke="#eb6c36"/>
  <text x="104" y="778" fill="#eb6c36" font-size="16" font-weight="600" font-family="'Geist Mono', monospace">maintenance_work_mem = 1 MB</text>
  <text x="976" y="778" fill="#eb6c36" font-size="16" font-weight="600" font-family="'Geist Mono', monospace" text-anchor="end">174,761 tuple slots</text>
  <g fill="#eb6c36"><rect x="104" y="836" width="156" height="74" rx="5"/><rect x="274" y="836" width="156" height="74" rx="5"/><rect x="444" y="836" width="156" height="74" rx="5"/><rect x="614" y="836" width="156" height="74" rx="5"/><rect x="784" y="836" width="156" height="74" rx="5"/></g>
  <g fill="#fff" font-size="17" font-weight="600" font-family="'Geist Mono', monospace" text-anchor="middle"><text x="182" y="881">pass 1</text><text x="352" y="881">pass 2</text><text x="522" y="881">pass 3</text><text x="692" y="881">pass 4</text><text x="862" y="881">pass 5</text></g>
  <text x="104" y="968" fill="#4f5d75" font-size="18" font-family="'Geist', sans-serif">Each fill pauses the heap scan and walks both indexes in full.</text>
  <rect x="72" y="1050" width="936" height="244" rx="8" fill="#fff" stroke="#bfc0c0"/>
  <text x="104" y="1098" fill="#2d3142" font-size="16" font-weight="600" font-family="'Geist Mono', monospace">maintenance_work_mem = 256 MB</text>
  <rect x="104" y="1150" width="836" height="74" rx="5" fill="#2d3142"/>
  <text x="522" y="1196" fill="#fff" font-size="18" font-weight="600" font-family="'Geist Mono', monospace" text-anchor="middle">1 complete index pass</text>
  <text x="104" y="1264" fill="#4f5d75" font-size="18" font-family="'Geist', sans-serif">The same 800,000 rows fit in one dead-tuple store.</text>
  <rect x="72" y="1330" width="936" height="96" rx="7" fill="#f5f5f5" stroke="rgba(45,49,66,.20)"/>
  <text x="540" y="1388" fill="#2d3142" font-size="19" font-weight="600" font-family="'Geist Mono', monospace" text-anchor="middle">cycles = ceil(800,000 / (174,761 − 291)) = 5</text>
  <line x1="72" y1="1510" x2="1008" y2="1510" stroke="rgba(45,49,66,.12)"/>
  <text x="72" y="1570" fill="#2d3142" font-size="27" font-weight="600" font-family="'Geist', sans-serif">The pass count is deterministic. Its cost depends on cache.</text>
  <text x="72" y="1655" fill="#7a8399" font-size="16" font-weight="500" font-family="'Geist Mono', monospace" letter-spacing=".12em">VACUUM MEMORY · CANERY</text>''',
        ),
        "story-04-name-the-process": story_shell(
            4,
            "Name the PostgreSQL process before tuning",
            "Four measured symptoms map to the backend, launcher, vacuum worker, WAL writer, and postmaster.",
            '''<text x="72" y="470" fill="#2d3142" font-size="70" font-family="'Instrument Serif', Georgia, serif">Name the process.</text>
  <text x="72" y="550" fill="#2d3142" font-size="70" font-family="'Instrument Serif', Georgia, serif">Then tune it.</text>
  <text x="72" y="650" fill="#4f5d75" font-size="26" font-family="'Geist', sans-serif">Four symptoms. Four different decisions inside one server.</text>
  <g font-family="'Geist', sans-serif">
    <rect x="72" y="720" width="448" height="250" rx="8" fill="#fff" stroke="#bfc0c0"/>
    <text x="104" y="766" fill="#7a8399" font-size="13" font-weight="600" font-family="'Geist Mono', monospace" letter-spacing=".12em">CONNECTION</text><text x="104" y="818" fill="#2d3142" font-size="30" font-weight="600">1.762 ms vs 0.0299 ms</text><text x="104" y="860" fill="#4f5d75" font-size="19">fresh backend vs reused connection</text><text x="104" y="922" fill="#eb6c36" font-size="18" font-weight="600">backend · pool connections</text>
    <rect x="560" y="720" width="448" height="250" rx="8" fill="#fff" stroke="#bfc0c0"/>
    <text x="592" y="766" fill="#7a8399" font-size="13" font-weight="600" font-family="'Geist Mono', monospace" letter-spacing=".12em">AUTOVACUUM ARRIVAL</text><text x="592" y="818" fill="#2d3142" font-size="30" font-weight="600">30.0 s wait · 0.03 s work</text><text x="592" y="860" fill="#4f5d75" font-size="19">qualified table waits for a visit</text><text x="592" y="922" fill="#eb6c36" font-size="18" font-weight="600">launcher · tune naptime</text>
    <rect x="72" y="1000" width="448" height="250" rx="8" fill="#fff" stroke="#bfc0c0"/>
    <text x="104" y="1046" fill="#7a8399" font-size="13" font-weight="600" font-family="'Geist Mono', monospace" letter-spacing=".12em">VACUUM PASSES</text><text x="104" y="1098" fill="#2d3142" font-size="30" font-weight="600">5 index scans vs 1</text><text x="104" y="1140" fill="#4f5d75" font-size="19">1 MB vs 256 MB work memory</text><text x="104" y="1202" fill="#eb6c36" font-size="18" font-weight="600">worker · size tuple memory</text>
    <rect x="560" y="1000" width="448" height="250" rx="8" fill="#fff" stroke="#bfc0c0"/>
    <text x="592" y="1046" fill="#7a8399" font-size="13" font-weight="600" font-family="'Geist Mono', monospace" letter-spacing=".12em">COMMIT PATH</text><text x="592" y="1098" fill="#2d3142" font-size="30" font-weight="600">5,000 syncs vs 2</text><text x="592" y="1140" fill="#4f5d75" font-size="19">synchronous_commit on vs off</text><text x="592" y="1202" fill="#eb6c36" font-size="18" font-weight="600">backend + WAL writer</text>
  </g>
  <rect x="72" y="1340" width="936" height="250" rx="10" fill="#2d3142"/>
  <text x="104" y="1390" fill="#bfc0c0" font-size="14" font-weight="600" font-family="'Geist Mono', monospace" letter-spacing=".12em">FULL 50-MINUTE TECHNICAL GUIDE</text>
  <text x="104" y="1450" fill="#fff" font-size="31" font-weight="600" font-family="'Geist', sans-serif">Postmaster · WAL · checkpoints · autovacuum</text>
  <text x="104" y="1496" fill="#fff" font-size="31" font-weight="600" font-family="'Geist', sans-serif">parallel workers · runnable PostgreSQL 16.2 lab</text>
  <text x="104" y="1556" fill="#eb6c36" font-size="23" font-weight="600" font-family="'Geist', sans-serif">Read the full article on Canery →</text>
  <text x="72" y="1655" fill="#eb6c36" font-size="16" font-weight="600" font-family="'Geist Mono', monospace" letter-spacing=".12em">LINK STICKER · READ THE ARTICLE</text>''',
        ),
    }
    for stem, source in stories.items():
        (SOCIAL / f"{stem}.html").write_text(source, encoding="utf-8")


def main() -> None:
    SOCIAL.mkdir(parents=True, exist_ok=True)
    build_feed()
    build_stories()
    print(f"wrote {len(FEED_SOURCES)} feed and 4 Story HTML sources to {SOCIAL}")


if __name__ == "__main__":
    main()
