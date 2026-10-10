#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for this article.

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


def logo_paths() -> str:
    source = (ROOT / "web/public/brand/canerly-lockup-horizontal.svg").read_text(encoding="utf-8")
    paths = re.findall(r"<path\b[\s\S]*?/>", source)
    if len(paths) != 2:
        raise RuntimeError("Could not read the canonical Canery horizontal lockup")
    return "\n".join(paths)


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
        height, logo_y, logo_width, scale = 1350, 72, 180, 0.2680965
        rule_y, title_y, title_size, title_gap = 150, 245, 58, 66
        deck_y = title_y + len(title) * title_gap + 20
        takeaway_rule, takeaway_y, footer_y = 1168, 1220, 1305
    else:
        height, logo_y, logo_width, scale = 1920, 250, 200, 0.297885
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
    footer = cta or "CUDA ARCHITECTURE REPAIRS · CANERY"
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
    visual += card(72, 500, 438, 300, "NVIDIA T4", ["compute capability 7.5", "real target: sm_75"],
                   tag="older than release")
    visual += card(570, 500, 438, 300, "GB10-class GPU", ["compute capability 12.1", "real target: sm_121"],
                   tag="newer than wheel", focal=True)
    visual += box(260, 850, 560, 100, fill="#ffffff", stroke=INK, rx=8)
    visual += mono(540, 892, "CUDA_ERROR_NO_BINARY_FOR_GPU", size=20, fill=INK, weight="600")
    visual += mono(540, 925, "same symptom · different broken layer", size=15, fill=ACCENT, weight="500")
    visual += label(291, 1015, "release validation / kernel path", size=13)
    visual += label(789, 1015, "binary code-image inventory", anchor="middle", size=13)
    emit("feed", 1, "one-error-two-causes",
         ["One CUDA error.", "Two opposite causes."],
         ["A T4 can be older than a serving release.", "An sm_121 GPU can be newer than its PyTorch wheel."],
         visual,
         ["Do not rebuild from the symptom.", "Find the lowest artifact without executable code."],
         total=6)


def feed_02():
    visual = ""
    layers = [
        ("MODEL + WORKLOAD", "adapter · precision · shapes"),
        ("SERVING RUNTIME", "TensorRT-LLM / TensorRT / ORT"),
        ("FRAMEWORK", "PyTorch build + native extensions"),
        ("CODE IMAGES", "cubin · compatible image · PTX"),
        ("COMPILER", "nvcc target inventory"),
        ("GPU + DRIVER", "sm_75 / sm_121 · driver ceiling"),
    ]
    y = 475
    for index, (name, detail) in enumerate(layers):
        focal = name == "CODE IMAGES"
        visual += box(150, y, 780, 82, fill=ACCENT_TINT if focal else "#ffffff",
                      stroke=ACCENT if focal else "rgba(45,49,66,0.28)", rx=7,
                      sw=1.4 if focal else 1)
        visual += label(178, y + 31, name, fill=ACCENT if focal else INK, size=13)
        visual += mono(902, y + 31, detail, size=13, fill=MUTED, anchor="end")
        if index < len(layers) - 1:
            visual += f'<line x1="540" y1="{y + 82}" x2="540" y2="{y + 98}" stroke="{RULE_SOLID}"/>'
        y += 98
    emit("feed", 2, "compatibility-is-a-stack",
         ["Compatibility is", "six separate gates."],
         ["Visibility, compilation, binary coverage, framework, runtime,", "and model support answer different questions."],
         visual,
         ["A green check at one layer cannot certify the next.", "Audit from hardware upward and stop at the first failure."],
         total=6)


def feed_03():
    visual = ""
    commands = [
        ("DEVICE", "torch.cuda.get_device_capability()"),
        ("INVENTORY", "torch.cuda.get_arch_list()"),
        ("PROOF", "(torch.ones(1, device='cuda') + 1).cpu()"),
    ]
    y = 500
    for index, (name, command) in enumerate(commands):
        focal = index == 2
        visual += card(72, y, 936, 126, command, ["observe, do not infer" if index < 2 else "synchronize a real core operation"],
                       focal=focal, tag=name)
        y += 148
    visual += label(72, 980, "loader selection", size=13)
    steps = ["exact cubin", "compatible image", "PTX JIT", "launch fails"]
    x = 72
    for index, step in enumerate(steps):
        w = 210
        visual += box(x, 1010, w, 70, fill=ACCENT_TINT if index == 3 else "#ffffff",
                      stroke=ACCENT if index == 3 else "rgba(45,49,66,0.28)", rx=7)
        visual += mono(x + w / 2, 1052, step, size=14,
                       fill=ACCENT if index == 3 else INK, weight="600")
        if index < 3:
            visual += txt(x + w + 12, 1054, "→", size=22, fill=MUTED, family=SANS)
        x += 242
    emit("feed", 3, "inspect-code-inventory",
         ["Enumeration is not", "execution proof."],
         ["A visible GPU can still reach a kernel with no compatible", "cubin or PTX image when the operation launches."],
         visual,
         ["A missing literal sm_121 string is not proof.", "Use the warning and a synchronized core CUDA operation."],
         total=6)


def feed_04():
    visual = ""
    steps = [
        ("1", "Install a compatible published wheel", "smallest replacement"),
        ("2", "Rebuild one failing extension", 'TORCH_CUDA_ARCH_LIST="7.5"'),
        ("3", "Rebuild PyTorch", "only when its core CUDA operation fails"),
        ("4", "Rebuild or change the runtime", "only when its native layer fails"),
    ]
    y = 470
    widths = [650, 720, 790, 860]
    for index, ((number, title, detail), width) in enumerate(zip(steps, widths)):
        focal = index == 1
        visual += box(72, y, width, 118, fill=ACCENT_TINT if focal else "#ffffff",
                      stroke=ACCENT if focal else "rgba(45,49,66,0.28)", rx=8)
        visual += mono(104, y + 42, number, size=20, fill=ACCENT if focal else SOFT, weight="600")
        visual += txt(148, y + 43, title, size=21, fill=INK, family=SANS, weight="600", anchor="start")
        visual += mono(148, y + 78, detail, size=14, fill=MUTED, anchor="start")
        y += 138
    emit("feed", 4, "smallest-valid-repair",
         ["Repair the smallest", "broken binary layer."],
         ["A framework rebuild is hours of change surface.", "An extension rebuild can be one isolated artefact."],
         visual,
         ["Core PyTorch passes but one .so fails? Rebuild that .so.", "Core PyTorch fails? Only then consider rebuilding PyTorch."],
         total=6)


def feed_05():
    visual = ""
    visual += card(72, 500, 280, 130, "HF checkpoint", ["pinned model revision"], tag="input")
    visual += f'<path d="M352 565 H420 V500 H470" fill="none" stroke="{MUTED}" stroke-width="2"/>'
    visual += f'<path d="M420 565 V820 H470" fill="none" stroke="{MUTED}" stroke-width="2"/>'
    visual += card(470, 440, 538, 220, "TensorRT-LLM 1.2", ["PyTorch execution backend", "supported HF checkpoint loads directly", "LLM(...) → trtllm-serve"],
                   focal=True, tag="llm-serving branch")
    visual += card(470, 750, 240, 190, "ONNX", ["versioned graph", "checker + shapes"], tag="interchange")
    visual += card(768, 750, 240, 190, "Generic runtime", ["TensorRT", "or ONNX Runtime"], tag="consumer")
    visual += f'<line x1="710" y1="845" x2="768" y2="845" stroke="{LINK}" stroke-width="2" marker-end="url(#arrow-link)"/>'
    visual += box(470, 990, 538, 86, fill="#ffffff", stroke=RULE_SOLID, rx=7)
    visual += mono(739, 1025, "ONNX is a sibling route — not a required TensorRT-LLM stage", size=14, fill=INK, weight="600")
    visual += mono(739, 1052, "do not insert stale trtllm-build steps into the 1.2 path", size=13, fill=ACCENT)
    emit("feed", 5, "choose-runtime-branch",
         ["TensorRT-LLM and ONNX", "are sibling routes."],
         ["TensorRT-LLM 1.2 loads supported checkpoints through PyTorch.", "ONNX feeds generic TensorRT or ONNX Runtime."],
         visual,
         ["Choose the branch your target runtime actually consumes.", "Then validate model, precision, shapes, and numerics."],
         total=6)


def feed_06():
    visual = ""
    items = [
        ("GPU", "name · count · UUID · compute capability"),
        ("STACK", "driver · Toolkit · PyTorch · runtime"),
        ("MODEL", "immutable revision · precision"),
        ("TRAFFIC", "input/output lengths · rate · concurrency"),
        ("POLICY", "warm-up · parallelism · KV-cache allocation"),
        ("METRICS", "TTFT · ITL · E2E latency · throughput"),
    ]
    for index, (name, detail) in enumerate(items):
        col, row = index % 2, index // 2
        x, y = 72 + col * 480, 490 + row * 170
        visual += card(x, y, 456, 145, name, [detail], focal=name == "METRICS", tag=f"{index + 1:02d}")
    visual += box(72, 1025, 936, 68, fill=INK, stroke=INK, rx=7)
    visual += mono(540, 1067, "NO STACK TUPLE → NO PERFORMANCE CLAIM", size=17, fill=PAPER, weight="600")
    emit("feed", 6, "measure-the-exact-stack",
         ["Benchmark the tuple.", "Not the product name."],
         ["Performance begins only after hardware, software, model,", "precision, traffic, and concurrency are fixed."],
         visual,
         ["The guide includes the audit, build gates, deployment branches,", "KV-cache math, and a reproducible benchmark schema."],
         total=6, cta="READ THE FULL GUIDE · CANERY.IN/BLOGS/ARCHITECTURE-AWARE-TENSORRT-LLM-CUDA-ONNX")


def story_01():
    visual = ""
    visual += card(72, 720, 936, 220, "Same launch symptom", ["CUDA_ERROR_NO_BINARY_FOR_GPU", "unsupported architecture warning"], focal=True, tag="what you see")
    visual += card(72, 995, 438, 250, "T4 · sm_75", ["older hardware", "release-validation gap", "possible compatible path"], tag="machine a")
    visual += card(570, 995, 438, 250, "GB10 · sm_121", ["newer hardware", "wheel-coverage gap", "core operation decides"], tag="machine b")
    visual += mono(540, 1330, "same error text ≠ same repair", size=21, fill=ACCENT, weight="600")
    emit("story", 1, "one-error-two-causes",
         ["One CUDA error.", "Two opposite causes."],
         ["An old GPU and a new GPU can fail at different", "layers of the same inference stack."],
         visual,
         ["Diagnose the loaded artefact before", "you rebuild the framework."],
         total=4)


def story_02():
    visual = ""
    rows = [
        ("GPU", "compute capability", "nvidia-smi + device query"),
        ("COMPILER", "target recognized", "nvcc --list-gpu-code"),
        ("BINARY", "compatible image", "cuobjdump / torch arch list"),
        ("CORE", "kernel executes", "synchronized tensor operation"),
        ("RUNTIME", "model path exists", "pinned support matrix"),
    ]
    y = 700
    for index, (layer, proof, command) in enumerate(rows):
        focal = layer == "CORE"
        visual += box(72, y, 936, 124, fill=ACCENT_TINT if focal else "#ffffff",
                      stroke=ACCENT if focal else "rgba(45,49,66,0.28)", rx=8)
        visual += label(100, y + 38, layer, fill=ACCENT if focal else INK, size=13)
        visual += txt(100, y + 76, proof, size=20, fill=INK, family=SANS, weight="600", anchor="start")
        visual += mono(980, y + 75, command, size=14, fill=MUTED, anchor="end")
        y += 144
    emit("story", 2, "audit-bottom-up",
         ["Audit the stack", "from the bottom up."],
         ["Each observation proves one boundary.", "Stop at the first layer without evidence."],
         visual,
         ["Visibility is not execution.", "Compilation is not product support."],
         total=4)


def story_03():
    visual = ""
    steps = [
        ("1", "Published wheel", "replace, then retest"),
        ("2", "One extension", "rebuild only the failing .so"),
        ("3", "PyTorch", "only if a core CUDA op fails"),
        ("4", "Serving runtime", "only if its native path fails"),
    ]
    y = 720
    for index, (number, name, detail) in enumerate(steps):
        w = 650 + index * 90
        focal = index == 1
        visual += box(72, y, w, 150, fill=ACCENT_TINT if focal else "#ffffff",
                      stroke=ACCENT if focal else "rgba(45,49,66,0.28)", rx=8)
        visual += mono(110, y + 58, number, size=24, fill=ACCENT if focal else SOFT, weight="600")
        visual += txt(160, y + 56, name, size=25, fill=INK, family=SANS, weight="600", anchor="start")
        visual += mono(160, y + 100, detail, size=16, fill=MUTED, anchor="start")
        y += 175
    emit("story", 3, "repair-smallest-layer",
         ["Repair the lowest", "broken layer."],
         ["Every broader rebuild increases cost, ABI risk,", "and the evidence you must collect again."],
         visual,
         ["Core works + extension fails?", "Rebuild the extension and stop."],
         total=4)


def story_04():
    visual = ""
    visual += card(72, 710, 936, 185, "Inside the full guide", ["read-only compatibility audit · build stop conditions", "TensorRT-LLM vs ONNX · KV-cache capacity math"], focal=True, tag="35-minute engineering guide")
    visual += card(72, 955, 438, 250, "Direct serving", ["HF checkpoint", "TensorRT-LLM 1.2", "PyTorch backend"], tag="branch a")
    visual += card(570, 955, 438, 250, "Graph interchange", ["PyTorch → ONNX", "TensorRT or ORT", "profiles + numerics"], tag="branch b")
    visual += box(170, 1280, 740, 100, fill=INK, stroke=INK, rx=10)
    visual += txt(540, 1323, "Read the full article on Canery", size=25, fill=PAPER, family=SANS, weight="600")
    visual += mono(540, 1355, "use the link sticker below", size=15, fill="#bfc0c0")
    emit("story", 4, "read-the-full-guide",
         ["Build only after", "the evidence says to."],
         ["From GPU architecture to model serving,", "the guide keeps every compatibility claim separate."],
         visual,
         ["Audit. Repair the smallest layer.", "Measure the exact stack."],
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
