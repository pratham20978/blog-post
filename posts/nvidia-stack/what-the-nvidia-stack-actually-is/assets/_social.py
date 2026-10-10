#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for this article.

Lockup widths are 220 (feed) and 245 (story), which is what
blog-forge/scripts/render_social.py locks. Scales are the part-6 values
multiplied by the same ratio, so the mark keeps its proportions.

NVIDIA Stack, part 1. Same construction as part 6 so the series reads as one set.

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
    footer = cta or "WHAT THE NVIDIA STACK ACTUALLY IS · CANERY.IN"
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




def feed_01():
    visual = ""
    names = [
        ("KERNEL MODULES", "nvidia.ko · nvidia-uvm.ko"),
        ("USER-MODE DRIVER", "libcuda.so.1"),
        ("CUDA RUNTIME", "libcudart.so.13"),
        ("COMPILER TOOLCHAIN", "nvcc · ptxas · nvlink"),
        ("ACCELERATED LIBRARIES", "libcublas.so.13 · libcudnn.so.9"),
    ]
    y = 500
    for index, (name, detail) in enumerate(names):
        focal = index < 2
        visual += box(120, y, 840, 96, fill=ACCENT_TINT if focal else "#ffffff",
                      stroke=ACCENT if focal else "rgba(45,49,66,0.28)", rx=7,
                      sw=1.4 if focal else 1)
        visual += label(150, y + 38, name, fill=ACCENT if focal else INK, size=13)
        visual += mono(930, y + 38, detail, size=14, fill=ACCENT if focal else MUTED, anchor="end")
        y += 112
    visual += mono(540, 1090, "five separately versioned artifacts, one word", size=19,
                   fill=ACCENT, weight="600")
    emit("feed", 1, "there-is-no-cuda",
         ["There is no", "single CUDA."],
         ["A kernel driver, a user-mode driver, a runtime, a compiler",
          "and a library portfolio. Four shippers, four schedules."],
         visual,
         ["Stop asking which CUDA version you have.",
          "Ask which artifact you are looking at."],
         total=6)


def feed_02():
    visual = ""
    visual += card(72, 500, 936, 210, "libcuda.so.1",
                   ["named by your framework's binaries",
                    "shipped by no wheel, ever"],
                   focal=True, tag="the host must supply this")
    visual += card(72, 745, 438, 240, "pip can deliver",
                   ["cuBLAS · cuDNN · NCCL", "the CUDA runtime", "nvcc, if you ask"],
                   tag="negotiable")
    visual += card(570, 745, 438, 240, "pip cannot",
                   ["the kernel modules", "the user-mode driver", "nothing substitutes"],
                   tag="not negotiable", focal=False)
    visual += box(230, 1020, 620, 96, fill="#ffffff", stroke=INK, rx=8)
    visual += mono(540, 1060, "4.86 GB of wheels", size=21, fill=INK, weight="600")
    visual += mono(540, 1092, "and none of it talks to the GPU", size=15, fill=ACCENT, weight="500")
    emit("feed", 2, "only-one-layer-is-mandatory",
         ["Only one layer", "must be on the box."],
         ["Thirty-two packages resolve inside the virtualenv.",
          "The library at the bottom of every chain does not."],
         visual,
         ["Everything above the driver is negotiable.",
          "The driver is not."],
         total=6)


def feed_03():
    visual = ""
    visual += label(72, 490, "what pytorch's own libraries carry")
    paths = [
        "$ORIGIN/../../nvidia/cudnn/lib",
        "$ORIGIN/../../nvidia/nccl/lib",
        "$ORIGIN/../../nvidia/cu13/lib",
        "$ORIGIN",
    ]
    visual += box(72, 520, 936, 300, fill="#ffffff", stroke=INK, rx=8)
    visual += label(104, 560, "DT_RPATH", fill=ACCENT, size=13)
    y = 610
    for path in paths:
        visual += mono(104, y, path, size=19, fill=INK, anchor="start")
        y += 46
    visual += card(72, 860, 936, 200, "The loader assembles it",
                   ["not the installer, not pip",
                    "resolved again, at import, by filename"],
                   focal=True, tag="every time you import torch")
    emit("feed", 3, "nothing-installs-this-stack",
         ["Nothing installs", "this stack."],
         ["Your CUDA install is a set of independently downloaded",
          "wheels that the dynamic loader stitches together."],
         visual,
         ["Resolution happens twice: once by pip,",
          "once by the loader, on different rules."],
         total=6)


def feed_04():
    visual = ""
    visual += label(72, 490, "inside cuda-toolkit==13.0.3")
    rows = [("nvidia-cublas", "13.1.1.3", True), ("nvidia-cuda-runtime", "13.0.96", False),
            ("nvidia-cusparse", "12.6.3.3", False), ("nvidia-cufft", "12.0.0.61", False),
            ("nvidia-curand", "10.4.0.35", True)]
    y = 520
    for name, version, focal in rows:
        visual += box(72, y, 936, 104, fill=ACCENT_TINT if focal else "#ffffff",
                      stroke=ACCENT if focal else "rgba(45,49,66,0.28)", rx=7,
                      sw=1.4 if focal else 1)
        visual += mono(104, y + 60, name, size=20, fill=ACCENT if focal else INK, anchor="start")
        visual += txt(976, y + 62, version, size=26, family=MONO, weight="600",
                      fill=ACCENT if focal else MUTED, anchor="end")
        y += 120
    visual += mono(540, 1140, "majors 10, 12 and 13 in one release", size=19,
                   fill=ACCENT, weight="600")
    emit("feed", 4, "one-release-three-majors",
         ["One Toolkit.", "Nine version streams."],
         ["Every component of a CUDA release carries its own",
          "version number, and they disagree with the release."],
         visual,
         ["No single number is “the CUDA version”.",
          "Name the artifact, then name its version."],
         total=6)


def feed_05():
    visual = ""
    visual += card(72, 500, 936, 170, "torch",
                   ["declares cuda-toolkit[…11] and four -cu13 wheels"],
                   tag="what you installed")
    visual += f'<line x1="540" y1="670" x2="540" y2="712" stroke="{RULE_SOLID}"/>'
    visual += card(72, 712, 936, 170, "nvidia-cudnn-cu13",
                   ["declared by torch, for convolutions"],
                   tag="pulled in")
    visual += f'<line x1="540" y1="882" x2="540" y2="924" stroke="{ACCENT}"/>'
    visual += card(72, 924, 936, 180, "nvidia-cublas",
                   ["545 MB of libcublasLt.so.13", "the library that runs your matmul"],
                   focal=True, tag="never asked for")
    emit("feed", 5, "cublas-arrives-sideways",
         ["cuBLAS is not", "a dependency of torch."],
         ["The library that actually multiplies your matrices",
          "arrives because cuDNN happens to depend on it."],
         visual,
         ["You are already using CUDA-X libraries",
          "you never installed and cannot name."],
         total=6)


def feed_06():
    visual = ""
    visual += label(72, 490, "no gpu, no driver, no toolkit")
    visual += box(72, 520, 936, 250, fill="#ffffff", stroke=INK, rx=8)
    visual += mono(104, 576, "$ python3 inspect_wheel.py torch 2.14.0", size=20,
                   fill=INK, anchor="start")
    visual += mono(104, 630, "download size  554.6 MB", size=17, fill=MUTED, anchor="start")
    visual += mono(104, 668, "entries        13,043", size=17, fill=MUTED, anchor="start")
    visual += mono(104, 706, "cost to list   3 range requests, 1.2 MB", size=17,
                   fill=ACCENT, anchor="start")
    visual += card(72, 810, 936, 250, "Read it before you install it",
                   ["a zip's central directory sits at the end of the file",
                    "so an HTTP Range request lists all of it",
                    "DT_NEEDED tells you what the loader will want"],
                   focal=True, tag="tier a lab")
    emit("feed", 6, "read-the-wheel-first",
         ["List a 554 MB wheel", "with 1.2 MB."],
         ["The whole stack can be inspected before any of it",
          "is installed, on a laptop with no NVIDIA GPU."],
         visual,
         ["Read Requires-Dist from the wheel,",
          "not from the API that describes it."],
         total=6)


def story_01():
    visual = ""
    visual += card(72, 736, 936, 210, "pip install torch", ["4.86 GB across 32 packages", "90 shared libraries"], focal=True, tag="what just happened")
    visual += card(72, 985, 936, 260, "Do I need the CUDA Toolkit?",
                   ["the most searched question in this stack",
                    "and it cannot be answered without a map",
                    "of what those gigabytes actually are"],
                   tag="the question you still cannot answer")
    visual += mono(540, 1330, "five different things are called CUDA", size=21,
                   fill=ACCENT, weight="600")
    emit("story", 1, "five-things-called-cuda",
         ["Five things are", "called “CUDA”."],
         ["A kernel driver, a user-mode driver, a runtime,",
          "a compiler toolchain and a library portfolio."],
         visual,
         ["None of them announces which one",
          "you are looking at."],
         total=4)


def story_02():
    visual = ""
    rows = [
        ("SERVING", "a container image", "separate products"),
        ("FRAMEWORK", "libtorch_cuda.so", "pip wheel"),
        ("LIBRARIES", "libcublas.so.13", "Toolkit or wheels"),
        ("RUNTIME", "libcudart.so.13", "Toolkit or wheel"),
        ("DRIVER", "libcuda.so.1", "NVIDIA driver"),
        ("KERNEL", "nvidia.ko", "NVIDIA driver"),
    ]
    y = 740
    for layer, artifact, ship in rows:
        focal = layer in ("DRIVER", "KERNEL")
        visual += box(72, y, 936, 104, fill=ACCENT_TINT if focal else "#ffffff",
                      stroke=ACCENT if focal else "rgba(45,49,66,0.28)", rx=8)
        visual += label(100, y + 32, layer, fill=ACCENT if focal else INK, size=13)
        visual += mono(100, y + 72, artifact, size=19, fill=INK, anchor="start")
        visual += mono(980, y + 71, ship, size=14, fill=ACCENT if focal else MUTED, anchor="end")
        y += 124
    emit("story", 2, "the-layer-map",
         ["Seven layers.", "Four shippers."],
         ["Read the right-hand column first.",
          "The layers are released separately, by different products."],
         visual,
         ["Only the bottom two must come",
          "from the machine itself."],
         total=4)


def story_03():
    visual = ""
    visual += card(72, 736, 936, 230, "What the wheel does NOT contain",
                   ["no cuBLAS, no cuDNN, no cudart, no cuFFT",
                    "13 shared objects, and not one of them is a math library"],
                   focal=True, tag="torch 2.14.0, 554.6 MB")
    visual += card(72, 996, 936, 200, "What it declares instead",
                   ["cuda-toolkit[cublas,cudart,cufft,cufile,cupti,",
                    "curand,cusolver,cusparse,nvjitlink,nvrtc,nvtx]"],
                   tag="requires-dist, from the archive itself")
    visual += box(170, 1232, 740, 110, fill="#ffffff", stroke=ACCENT, rx=8)
    visual += mono(540, 1274, "no package name here begins with nvidia-", size=19,
                   fill=ACCENT, weight="600")
    visual += mono(540, 1310, "read the whole line, from the wheel itself", size=15, fill=MUTED)
    emit("story", 3, "read-the-wheel",
         ["cuBLAS hides", "inside a bracket."],
         ["Filter a dependency list on the prefix nvidia- and",
          "cuBLAS vanishes. It did not go anywhere."],
         visual,
         ["Two independent passes of this",
          "research made that exact mistake."],
         total=4)


def story_04():
    visual = ""
    visual += card(72, 736, 936, 210, "Inside the article",
                   ["the layer map · one matmul traced down nine steps",
                    "what the driver installs · installer, wheel or container"],
                   focal=True, tag="18-minute read, part 1 of the series")
    visual += card(72, 986, 438, 260, "Runnable, no GPU",
                   ["inspect_wheel.py", "resolve_stack.py", "python3 and a network"],
                   tag="tier a lab")
    visual += card(570, 986, 438, 260, "Next in the series",
                   ["the four CUDA", "version numbers", "and which one decides"],
                   tag="part 2")
    visual += box(170, 1286, 740, 104, fill=INK, stroke=INK, rx=10)
    visual += txt(540, 1329, "Read the full article on Canery", size=25, fill=PAPER,
                  family=SANS, weight="600")
    visual += mono(540, 1363, "use the link sticker below", size=15, fill="#bfc0c0")
    emit("story", 4, "read-the-full-article",
         ["Learn the map", "before the failures."],
         ["Every hard failure in this stack gets diagnosed at the",
          "wrong layer by someone who never had the map."],
         visual,
         ["Name the layer. Name the artifact.",
          "Then decide what to install."],
         total=4, cta="LINK STICKER · READ THE ARTICLE")


BUILDERS = [
    feed_01, feed_02, feed_03, feed_04, feed_05, feed_06,
    story_01, story_02, story_03, story_04,
]


if __name__ == "__main__":
    requested = set(sys.argv[1:])
    for builder in BUILDERS:
        name = builder.__name__.replace("_", "-")
        if not requested or name in requested:
            builder()
