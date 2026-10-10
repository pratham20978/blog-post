#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for this article.

Lockup widths are 220 (feed) and 245 (story), which is what
blog-forge/scripts/render_social.py locks. Scales are the part-6 values
multiplied by the same ratio, so the mark keeps its proportions.

NVIDIA Stack, part 2. Same construction as parts 1 and 6 so the series reads as one set.

The shared feed is 1080x1350 for Instagram and LinkedIn. Story frames are
independently composed at 1080x1920. This script writes editable HTML only;
Blog Forge's render_social.py exports the standalone SVG and exact-size PNG.
"""

from __future__ import annotations

import pathlib
import re
import sys

from _build import (
    ACCENT,
    ACCENT_TINT,
    DEFS,
    FONTS,
    INK,
    LINK,
    MONO,
    MUTED,
    PAPER,
    RULE,
    RULE_SOLID,
    SANS,
    SERIF,
    SOFT,
    box,
    esc,
    mono,
    txt,
)

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "social"
ROOT = HERE.parents[3]
VW = 1080


# The brand lockup ships as bird + "Canery" only. Every social frame must read
# "canery.in", so the domain suffix is drawn here in the lockup's own coordinate
# space, on the wordmark's baseline and at its cap height.
LOCKUP_VIEWBOX_W = 671.40      # the source lockup's own width
IN_GAP = -10                   # the source viewBox has trailing padding; close it up
IN_SIZE = 140                  # matches the wordmark's cap height
IN_ADVANCE = 171               # measured advance of ".in" in Geist 600 at IN_SIZE
LOCKUP_FULL_W = LOCKUP_VIEWBOX_W + IN_GAP + IN_ADVANCE


def logo_paths() -> str:
    source = (ROOT / "web/public/brand/canerly-lockup-horizontal.svg").read_text(encoding="utf-8")
    paths = re.findall(r"<path\b[\s\S]*?/>", source)
    if len(paths) != 2:
        raise RuntimeError("Could not read the canonical Canery horizontal lockup")
    suffix = (
        f'<text x="{LOCKUP_VIEWBOX_W + IN_GAP}" y="122.5" font-size="{IN_SIZE}" '
        f'font-family="{SANS}" font-weight="600" text-anchor="start">.in</text>'
    )
    return "\n".join(paths) + "\n" + suffix


LOGO_PATHS = logo_paths()


def lines(x, y, values, *, size, family=SANS, fill=INK, weight="400", gap=None, anchor="start"):
    gap = gap or int(size * 1.16)
    return "".join(
        txt(x, y + index * gap, value, size=size, fill=fill, family=family,
            weight=weight, anchor=anchor)
        for index, value in enumerate(values)
    )


def label(x, y, value, *, fill=SOFT, anchor="start", size=14):
    return mono(x, y, value.upper(), size=size, fill=fill, anchor=anchor,
                weight="500", track="0.12em")


def card(x, y, w, h, title, detail, *, focal=False, tag=None):
    stroke = ACCENT if focal else "rgba(45,49,66,0.28)"
    fill = ACCENT_TINT if focal else "#ffffff"
    result = box(x, y, w, h, fill=fill, stroke=stroke, rx=8, sw=1.2 if focal else 1)
    if tag:
        result += label(x + 22, y + 28, tag, fill=ACCENT if focal else SOFT, size=12)
    result += txt(x + 22, y + 60, title, size=22, fill=ACCENT if focal else INK,
                  family=SANS, weight="600", anchor="start")
    if isinstance(detail, str):
        detail = [detail]
    result += lines(x + 22, y + 92, detail, size=15, family=MONO, fill=MUTED, gap=23)
    return result


def shell(kind, number, total, title, deck, visual, takeaway, *, cta=None):
    if kind == "feed":
        height, logo_y, logo_width, scale = 1350, 72, 220, 220 / LOCKUP_FULL_W
        rule_y, title_y, title_size, title_gap = 150, 245, 58, 66
        deck_y = title_y + len(title) * title_gap + 20
        takeaway_rule, takeaway_y, footer_y = 1168, 1220, 1305
    else:
        height, logo_y, logo_width, scale = 1920, 250, 245, 245 / LOCKUP_FULL_W
        rule_y, title_y, title_size, title_gap = 340, 470, 70, 80
        deck_y = title_y + len(title) * title_gap + 28
        takeaway_rule, takeaway_y, footer_y = 1505, 1570, 1665

    defs = DEFS
    logo = (
        f'<g data-canery-logo="lockup" data-logo-x="72" data-logo-y="{logo_y}" '
        f'data-logo-width="{logo_width}" fill="{INK}" '
        f'transform="translate(72 {logo_y}) scale({scale})">{LOGO_PATHS}</g>'
    )
    body = f'<rect width="{VW}" height="{height}" fill="{PAPER}"/>'
    body += logo
    body += label(1008, logo_y + 35, f"{number:02d} / {total:02d}", anchor="end", size=15)
    body += f'<line x1="72" y1="{rule_y}" x2="1008" y2="{rule_y}" stroke="{RULE}"/>'
    body += lines(72, title_y, title, size=title_size, family=SERIF, gap=title_gap)
    body += lines(72, deck_y, deck, size=22 if kind == "feed" else 26,
                  fill=MUTED, gap=30 if kind == "feed" else 36)
    body += visual
    body += f'<line x1="72" y1="{takeaway_rule}" x2="1008" y2="{takeaway_rule}" stroke="{RULE}"/>'
    body += lines(72, takeaway_y, takeaway, size=22 if kind == "feed" else 27,
                  weight="600", gap=30 if kind == "feed" else 36)
    footer = cta or "THE FOUR CUDA VERSION NUMBERS · CANERY.IN"
    body += label(72, footer_y, footer, fill=ACCENT if cta else SOFT,
                  size=14 if kind == "feed" else 16)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VW} {height}" '
        f'width="{VW}" height="{height}" role="img">\n{defs}\n{body}\n</svg>'
    )


def emit(kind, number, slug, title, deck, visual, takeaway, *, total, cta=None):
    svg = shell(kind, number, total, title, deck, visual, takeaway, cta=cta)
    html = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f'<title>{esc(" ".join(title))}</title><link href="{FONTS}" rel="stylesheet">'
        f'<style>html,body{{margin:0;background:{PAPER}}}svg{{display:block}}</style>'
        f'</head><body>{svg}</body></html>'
    )
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{kind}-{number:02d}-{slug}.html"
    path.write_text(html, encoding="utf-8")
    print(path.name)




PLATES = [
    ("1", "nvidia.ko", "580.65.06", "kernel-mode driver", False),
    ("2", "libcuda.so.1", "13.0", "CUDA user-mode driver", True),
    ("3", "libcudart.so.13", "13.0", "CUDA runtime, in the wheel", True),
    ("4", "nvcc", "13.4", "Toolkit compiler", False),
]


def feed_01():
    visual = ""
    y = 500
    for idx, name, value, role, decisive in PLATES:
        visual += box(120, y, 840, 96, fill=ACCENT_TINT if decisive else "#ffffff",
                      stroke=ACCENT if decisive else "rgba(45,49,66,0.28)", rx=7,
                      sw=1.4 if decisive else 1)
        visual += label(150, y + 40, f"{idx}  {role}", fill=ACCENT if decisive else INK, size=13)
        visual += mono(930, y + 40, f"{name}  {value}", size=14,
                       fill=ACCENT if decisive else MUTED, anchor="end")
        y += 112
    visual += mono(540, 1090, "only the middle two decide whether your code runs",
                   size=19, fill=ACCENT, weight="600")
    emit("feed", 1, "four-numbers",
         ["Four numbers,", "one word."],
         ["Kernel driver, user-mode driver, runtime, compiler.",
          "All four are correctly called \u201cthe CUDA version\u201d."],
         visual,
         ["Two of them decide whether you run.",
          "The one you check first is not either."],
         total=6)


def feed_02():
    visual = ""
    visual += card(72, 500, 936, 230, "nvidia-smi says CUDA 13.0",
                   ["that is a ceiling, not an inventory",
                    "NVIDIA renamed the field CUDA UMD Version"],
                   focal=True, tag="the number everyone misreads")
    visual += card(72, 765, 438, 250, "what it means",
                   ["the newest CUDA this", "driver will serve"],
                   tag="a ceiling")
    visual += card(570, 765, 438, 250, "what it does not",
                   ["say a Toolkit is", "installed anywhere"],
                   tag="not an inventory")
    visual += box(230, 1050, 620, 80, fill="#ffffff", stroke=INK, rx=8)
    visual += mono(540, 1100, "a wheel-only box has no Toolkit at all", size=17,
                   fill=ACCENT, weight="600")
    emit("feed", 2, "a-ceiling-not-an-inventory",
         ["It is a ceiling,", "not an inventory."],
         ["NVIDIA deprecated the field name to say exactly this.",
          "It is now CUDA UMD Version \u2014 user-mode driver."],
         visual,
         ["Your driver reporting 13.0 has not",
          "installed CUDA 13.0 anywhere."],
         total=6)


def feed_03():
    visual = ""
    visual += label(72, 490, "one host, one application, one comparison")
    visual += box(72, 520, 936, 300, fill="#ffffff", stroke=INK, rx=8)
    rows = [
        ("driver ceiling", "13.0", "from libcuda.so.1", False),
        ("application runtime", "13.4", "a compile-time constant", True),
        ("verdict", "runs", "minor version compatibility", True),
    ]
    y = 590
    for name, value, note, focal in rows:
        visual += label(104, y, name, fill=ACCENT if focal else SOFT, size=13)
        visual += mono(560, y + 4, value, size=26,
                       fill=ACCENT if focal else INK, anchor="end", weight="600")
        visual += mono(976, y + 4, note, size=14, fill=MUTED, anchor="end")
        y += 90
    visual += card(72, 860, 936, 200, "The runtime is AHEAD of the ceiling",
                   ["and that is the case the rule was built for",
                    "so long as the major version matches"],
                   focal=True, tag="not the failure case")
    emit("feed", 3, "ahead-of-the-ceiling",
         ["Newer than the", "driver, and fine."],
         ["A CUDA 13.4 build on a driver reporting 13.0.",
          "NVIDIA publishes this exact case as a passing run."],
         visual,
         ["Leaving the major family is the failure.",
          "Being ahead of the ceiling is not."],
         total=6)


def feed_04():
    visual = ""
    visual += label(72, 490, "minimum driver branch, by cuda major family")
    bands = [("CUDA 11.x", "driver \u2265 450", 300), ("CUDA 12.x", "driver \u2265 525", 560),
             ("CUDA 13.x", "driver \u2265 580", 840)]
    y = 530
    for name, rule, width in bands:
        focal = name.startswith("CUDA 13")
        visual += box(120, y, width, 96, fill=ACCENT_TINT if focal else "#ffffff",
                      stroke=ACCENT if focal else "rgba(45,49,66,0.28)", rx=7,
                      sw=1.4 if focal else 1)
        visual += label(150, y + 40, name, fill=ACCENT if focal else INK, size=13)
        visual += mono(120 + width - 30, y + 40, rule, size=15,
                       fill=ACCENT if focal else MUTED, anchor="end")
        y += 118
    visual += card(72, 900, 936, 190, "Three numbers, not a matrix",
                   ["the minimum is per major FAMILY, not per release",
                    "which is what changed at CUDA 11"],
                   focal=True, tag="what to memorise")
    emit("feed", 4, "three-floors",
         ["Three floors.", "That is the table."],
         ["Every release-by-release compatibility matrix you have",
          "bookmarked collapses into three driver branches."],
         visual,
         ["450, 525, 580. Clear the floor for your",
          "major family and the minor version is free."],
         total=6)


def feed_05():
    visual = ""
    visual += card(72, 490, 936, 200, "cuda-compat-13-4",
                   ["replaces libcuda.so.1, leaves nvidia.ko alone",
                    "which is why change control can accept it"],
                   focal=True, tag="the forward-compatibility package")
    visual += label(72, 740, "and the preconditions nobody quotes")
    items = [
        "data center GPUs, some NGC RTX SKUs, Jetson \u2014 that is the list",
        "installing it does nothing until you set LD_LIBRARY_PATH",
        "no CUDA\u2013OpenGL or Vulkan interop, in any major family",
        "an older package is unsupported on a newer driver",
    ]
    visual += box(72, 770, 936, 290, fill="#ffffff", stroke=INK, rx=8)
    y = 830
    for item in items:
        visual += mono(104, y, f"\u00b7  {item}", size=15, fill=INK, anchor="start")
        y += 58
    visual += mono(540, 1105, "an ordinary consumer card is not on that list", size=17,
                   fill=ACCENT, weight="600")
    emit("feed", 5, "forward-compat-preconditions",
         ["The package has", "four preconditions."],
         ["Forward compatibility spans a different boundary \u2014",
          "kernel driver to CUDA driver, not runtime to driver."],
         visual,
         ["It is a datacenter answer to a frozen driver,",
          "not a general fix for an old one."],
         total=6)


def feed_06():
    visual = ""
    visual += label(72, 490, "one pip install torch, six version strings")
    rows = [("2.14.0", "PyPI distribution"), ("2.14.0+cu130", "torch.__version__"),
            ("13.0", "torch.version.cuda"), ("13.0.3", "cuda-toolkit pin"),
            ("13.0.96", "nvidia-cuda-runtime pin"), ("13000", "CUDART_VERSION")]
    visual += box(72, 520, 936, 430, fill="#ffffff", stroke=INK, rx=8)
    y = 580
    for value, namespace in rows:
        focal = value in ("2.14.0+cu130", "13000")
        visual += mono(104, y, value, size=20, fill=ACCENT if focal else INK,
                       anchor="start", weight="600" if focal else "400")
        visual += mono(976, y, namespace, size=15, fill=MUTED, anchor="end")
        y += 62
    visual += card(72, 985, 936, 130, "Only the last one is compared",
                   ["against anything at all"], focal=True)
    emit("feed", 6, "read-the-article",
         ["Six strings.", "One install."],
         ["Which of them your program is actually checked",
          "against \u2014 and the three floors that decide it."],
         visual,
         ["The full article walks all four numbers",
          "to the file that produced each one."],
         total=6, cta="READ IT AT CANERY.IN/BLOGS/FOUR-CUDA-VERSION-NUMBERS")


def story_01():
    visual = ""
    visual += card(72, 736, 936, 220, "nvidia-smi says 13.0",
                   ["nvcc --version says 13.4", "torch.version.cuda says 13.0"],
                   focal=True, tag="one machine, three answers")
    visual += card(72, 995, 936, 250, "All three are correct.",
                   ["and none of them answers the question",
                    "you actually have: will this wheel run",
                    "on this driver?"],
                   tag="the unhelpful truth")
    visual += mono(540, 1330, "four numbers, and only two decide", size=21,
                   fill=ACCENT, weight="600")
    emit("story", 1, "three-answers",
         ["One machine,", "three answers."],
         ["Every command is telling the truth about a",
          "different artifact. That is the whole problem."],
         visual,
         ["Two of the four decide whether",
          "your code runs."],
         total=4)


def story_02():
    visual = ""
    visual += label(72, 770, "what nvidia-smi is actually reporting")
    visual += box(72, 810, 936, 300, fill="#ffffff", stroke=INK, rx=8)
    visual += label(104, 866, "CUDA UMD VERSION", fill=ACCENT, size=15)
    visual += mono(104, 932, "the latest CUDA version", size=22, fill=INK, anchor="start")
    visual += mono(104, 977, "supported by the driver", size=22, fill=INK, anchor="start")
    visual += mono(104, 1048, "NVIDIA's own wording", size=15, fill=SOFT, anchor="start")
    visual += card(72, 1150, 936, 230, "It is a ceiling.",
                   ["Not a list of what is installed.",
                    "A wheel-only box has no Toolkit at all."],
                   focal=True, tag="read it this way")
    emit("story", 2, "a-ceiling",
         ["A ceiling, not", "an inventory."],
         ["NVIDIA deprecated the old field name",
          "to say exactly this."],
         visual,
         ["Your driver reporting 13.0 has not",
          "installed CUDA 13.0 anywhere."],
         total=4)


def story_03():
    visual = ""
    visual += label(72, 780, "the entire compatibility table")
    rows = [("CUDA 11.x", "driver \u2265 450"), ("CUDA 12.x", "driver \u2265 525"),
            ("CUDA 13.x", "driver \u2265 580")]
    y = 820
    for name, rule in rows:
        focal = name.startswith("CUDA 13")
        visual += box(72, y, 936, 110, fill=ACCENT_TINT if focal else "#ffffff",
                      stroke=ACCENT if focal else "rgba(45,49,66,0.28)", rx=8,
                      sw=1.4 if focal else 1)
        visual += label(110, y + 48, name, fill=ACCENT if focal else INK, size=15)
        visual += mono(970, y + 48, rule, size=20,
                       fill=ACCENT if focal else MUTED, anchor="end")
        y += 130
    visual += mono(540, 1270, "per major family, never per release", size=21,
                   fill=ACCENT, weight="600")
    visual += mono(540, 1320, "and the minor version is then free", size=17, fill=MUTED)
    emit("story", 3, "three-floors",
         ["Three floors.", "That is the table."],
         ["A CUDA 13.4 build runs on a driver",
          "reporting 13.0. By design."],
         visual,
         ["Clear your major family's floor and",
          "the minor version stops mattering."],
         total=4)


def story_04():
    visual = ""
    visual += card(72, 760, 936, 250, "Read CUDART_VERSION",
                   ["out of the wheel, before you install it",
                    "then compare it with the driver's ceiling"],
                   focal=True, tag="predict, do not diagnose")
    visual += label(72, 1065, "the lab needs no gpu, no driver, no toolkit")
    visual += box(72, 1105, 936, 260, fill="#ffffff", stroke=INK, rx=8)
    visual += mono(104, 1170, "CUDART_VERSION   13000", size=19, fill=INK, anchor="start")
    visual += mono(104, 1220, "cudaRuntimeGetVersion()", size=19, fill=INK, anchor="start")
    visual += mono(104, 1270, "  -> 13000, on a machine", size=19, fill=ACCENT, anchor="start")
    visual += mono(104, 1315, "     with no NVIDIA driver", size=19, fill=ACCENT, anchor="start")
    emit("story", 4, "read-the-article",
         ["Predict it before", "you install."],
         ["Two scripts, no GPU required, and every",
          "number in the article traced to a file."],
         visual,
         ["The full article is on Canery."],
         total=4, cta="LINK IN THE STICKER ABOVE")


BUILDERS = [feed_01, feed_02, feed_03, feed_04, feed_05, feed_06,
            story_01, story_02, story_03, story_04]


if __name__ == "__main__":
    requested = set(sys.argv[1:])
    for builder in BUILDERS:
        name = builder.__name__.replace("_", "-")
        if not requested or name in requested:
            builder()
