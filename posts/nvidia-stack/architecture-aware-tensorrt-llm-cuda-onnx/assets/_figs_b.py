#!/usr/bin/env python3
"""Figures 09-16 for architecture-aware-tensorrt-llm-cuda-onnx."""
import sys

from _build import (ACCENT, ACCENT_TINT, INK, LINK, MONO, MUTED, PAPER, PAPER2, RULE,
                    RULE_SOLID, SANS, SERIF, SOFT, alabel, box, callout, chip, diamond,
                    elbow, elbow_hvh, elbow_vh, emit, eyebrow, hbracket, hline, legend,
                    mark, masked, mono, node, oval, tag, txt, vbracket, vhv, vline)


# ------------------------------------------------------------------ FIG 09
def fig09():
    """Evidence matrix: which rows a given repair forces you to re-collect."""
    vw, vh = 1016, 492
    s = eyebrow(64, 44, "layer")
    s += eyebrow(248, 44, "authoritative observation")

    rows = [  # top = highest layer
        ("Serving runtime", "server log · precision · shapes · free memory"),
        ("Model integration", "immutable revision · release model table"),
        ("Extension", "build log · ldd · extension smoke test"),
        ("PyTorch binary", "torch.version.cuda · get_arch_list() · sync op"),
        ("Toolkit / compiler", "readlink -f nvcc · --list-gpu-code"),
        ("Driver", "driver version · compatibility matrix"),
        ("Device assignment", "GPU UUID · compute_cap · CUDA_VISIBLE_DEVICES"),
        ("Host", "uname -m · python platform · wheel tags"),
    ]
    # which rows each repair invalidates (index into rows)
    cols = [
        (704, "swap the", "torch wheel", {3, 2, 0}, MUTED),
        (800, "rebuild one", "extension", {2}, ACCENT),
        (896, "rebuild", "PyTorch", {4, 3, 2, 0}, MUTED),
    ]
    for cx, a, b, _, c in cols:
        s += mono(cx, 36, a, size=8, fill=c if c == ACCENT else SOFT, track="0.10em")
        s += mono(cx, 48, b, size=8, fill=c if c == ACCENT else SOFT, track="0.10em")
    s += hbracket(656, 944, 60, "", colour=RULE_SOLID, below=False, arm=6)
    s += mono(800, 74, "re-collect after", size=8, fill=SOFT, track="0.14em")

    y0, rh = 88, 36
    s += f'<rect x="64" y="{y0}" width="888" height="{rh * 8}" rx="4" fill="#ffffff" stroke="{INK}" stroke-width="1"/>'
    for i, (name, ev) in enumerate(rows):
        y = y0 + i * rh
        if i % 2 == 1:
            s += f'<rect x="65" y="{y}" width="886" height="{rh}" fill="{PAPER2}" fill-opacity="0.55"/>'
        if i:
            s += f'<line x1="64" y1="{y}" x2="952" y2="{y}" stroke="{RULE}" stroke-width="1"/>'
        s += txt(80, y + rh / 2 + 4, name, size=12, weight="600", fill=INK, anchor="start")
        s += mono(248, y + rh / 2 + 3, ev, size=9, fill=MUTED, anchor="start")
        for cx, _, _, hit, c in cols:
            cy = y + rh / 2
            if i in hit:
                s += f'<rect x="{cx - 6}" y="{cy - 6}" width="12" height="12" rx="2" fill="{c}"/>'
            else:
                s += f'<rect x="{cx - 5}" y="{cy - 5}" width="10" height="10" rx="2" fill="none" stroke="{SOFT}" stroke-width="1"/>'
    s += f'<line x1="656" y1="{y0}" x2="656" y2="{y0 + rh * 8}" stroke="{RULE}" stroke-width="1"/>'

    s += callout(952, 412, "rows below the change keep their evidence",
                 896, y0 + 5 * rh + rh / 2 + 8, colour=INK, anchor="end",
                 leader=(944, 416), cx=930, cy=380)
    s += legend(448, vw, [("re-collect this row", INK, "box"),
                          ("evidence still valid", SOFT, "hollow"),
                          ("the smallest repair", ACCENT, "box")])
    return emit("09", "evidence-matrix", "Every layer needs different evidence",
                "Keep every row. A later package change invalidates only the rows it "
                "touches — and the audit tells you which.",
                "evidence", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    """Where the process died names the artifact that owns the repair."""
    vw, vh = 1016, 404
    s = eyebrow(32, 44, "how far the process got before it failed")
    s += hline(48, 976, 72, stroke=RULE_SOLID, marker="arrow")

    phases = [
        ("configure", "Compile", "nvcc fatal :", "unsupported gpu architecture",
         "the selected nvcc", "rebuild PyTorch", False),
        ("import", "Load", "undefined symbol :", "_ZN3c10 ... torch ABI",
         "that extension build", "add arch flags", False),
        ("first sync op", "Launch", "no kernel image is", "available for execution",
         "the PyTorch wheel", "rebuild the extension", True),
        ("model load", "Construct", "unknown architecture", "or feature combination",
         "the release model table", "recompile anything", False),
        ("request", "Serve", "OOM \u00b7 shape assert \u00b7", "fallback warning",
         "runtime config + memory", "blame the SM", False),
    ]
    top, w, pitch, ch = 104, 176, 184, 92
    for i, (ph, verb, sig1, sig2, owner, wrong, focal) in enumerate(phases):
        x = 64 + i * pitch
        cx = x + w / 2
        col = ACCENT if focal else INK
        s += f'<circle cx="{cx}" cy="72" r="{5 if focal else 4}" fill="{col}"/>'
        s += mono(cx, 60, ph, size=8, fill=ACCENT if focal else SOFT, track="0.10em")
        s += vline(cx, 80, top - 4, stroke=ACCENT if focal else RULE_SOLID, sw=1,
                   marker=None, dash="3,3")
        s += box(x, top, w, ch, fill=ACCENT_TINT if focal else "#ffffff", stroke=col)
        s += txt(cx, top + 26, verb, size=12, weight="600", fill=col)
        s += f'<line x1="{x + 16}" y1="{top + 40}" x2="{x + w - 16}" y2="{top + 40}" stroke="{RULE}" stroke-width="0.8"/>'
        s += mono(cx, top + 60, sig1, size=8, fill=MUTED)
        s += mono(cx, top + 74, sig2, size=8, fill=MUTED)
        oy = top + ch + 30
        s += box(x, oy, w, 44, fill=ACCENT_TINT if focal else "rgba(45,49,66,0.05)",
                 stroke=ACCENT if focal else MUTED)
        s += mono(cx, oy + 18, "owns the repair", size=7, fill=SOFT, track="0.12em")
        s += txt(cx, oy + 34, owner, size=10, weight="500", fill=col)
        s += vline(cx, top + ch, oy - 2, stroke=ACCENT if focal else MUTED, sw=1)
        wy = oy + 70
        s += mark(x + 14, wy, False, colour=SOFT, size=9)
        s += txt(x + 28, wy + 4, wrong, size=10, fill=SOFT, anchor="start")
        s += (f'<line x1="{x + 26}" y1="{wy + 1}" x2="{x + 28 + 5.4 * len(wrong)}" '
              f'y2="{wy + 1}" stroke="{SOFT}" stroke-width="0.9"/>')

    s += eyebrow(32, top + ch + 104, "wrong", fill=SOFT)
    floor = 344
    s += f'<line x1="48" y1="{floor}" x2="{vw - 48}" y2="{floor}" stroke="{INK}" stroke-width="1"/>'
    s += eyebrow(64, floor + 24, "keep", fill=SOFT)
    s += txt(116, floor + 25, "the earliest precise message \u2014 before a framework catches, retries or "
             "wraps it \u2014 and the smallest command that still passed one boundary below",
             size=11, fill=MUTED, anchor="start")
    return emit("10", "failure-phase-ownership", "Where it failed names what to repair",
                "Five failure phases, five different owning artifacts. Collapsing them into "
                "one ticket is how teams rebuild the largest component instead of the broken one.",
                "ownership", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    """Repair ladder: five steps, rising change surface, one place to start."""
    vw, vh = 1016, 440
    s = eyebrow(32, 44, "change surface")
    s += hline(160, 976, 40, stroke=RULE_SOLID, marker="arrow")

    floor = 372
    steps = [
        ("repair 0", "Replace the artifact", ["another wheel family covers", "the GPU, or the release container"],
         "minutes · new environment", True),
        ("repair 1", "Rebuild one extension", ["core op passes,", "one extension fails"],
         "TORCH_CUDA_ARCH_LIST · same ABI", False),
        ("repair 2", "Rebuild PyTorch", ["core op fails and no wheel", "satisfies the version pin"],
         "pinned commit · hours · big disk", False),
        ("repair 3", "Rebuild TensorRT-LLM", ["PyTorch path works, a native", "TensorRT-LLM layer is uncovered"],
         "build_wheel.py · ~63 GB image", False),
        ("repair 4", "Pin another product path", ["compiler or release dropped", "the SM, model, or feature"],
         "older tuple · ORT · plain torch", False),
    ]
    for i, (t, name, trig, cost, focal) in enumerate(steps):
        x, w = 64 + i * 184, 176
        top = 252 - i * 40
        s += box(x, top, w, floor - top, fill=ACCENT_TINT if focal else "#ffffff",
                 stroke=ACCENT if focal else INK)
        s += tag(x + 8, top + 8, t, stroke=ACCENT if focal else INK)
        s += txt(x + w / 2, top + 40, name, size=12, weight="600",
                 fill=ACCENT if focal else INK)
        for j, line in enumerate(trig):
            s += mono(x + w / 2, top + 58 + j * 12, line, size=8, fill=MUTED)
        s += mono(x + w / 2, top + 92, cost, size=8, fill=SOFT)
    s += f'<line x1="48" y1="{floor}" x2="{vw - 48}" y2="{floor}" stroke="{INK}" stroke-width="1"/>'
    s += eyebrow(64, floor + 24, "trigger", fill=SOFT)
    s += txt(128, floor + 25, "the failing test names this artifact — never the device name alone",
             size=11, fill=MUTED, anchor="start")
    s += callout(72, 196, "start here", 64 + 88, 252 - 2, colour=ACCENT, anchor="start",
                 leader=(80, 202), cx=96, cy=240)
    return emit("11", "repair-ladder", "Repair the lowest broken layer",
                "Replace before rebuild; one extension before the framework; the framework "
                "before the serving runtime.",
                "policy", vw, vh, s)


# ------------------------------------------------------------------ FIG 12
def fig12():
    """A controlled PyTorch source build, as a two-row snake."""
    vw, vh = 1016, 380
    s = eyebrow(32, 44, "six stages, one deliverable")

    bw, bh = 224, 72
    top, bot = 80, 208
    stages = [
        (48, top, "01", "Pin the source", "git checkout <commit> · submodules", "backend"),
        (368, top, "02", "Prove the target", "nvcc --list-gpu-code · cpp_extension.py", "backend"),
        (688, top, "03", "Configure the frontend", "TORCH_CUDA_ARCH_LIST=12.1 · pip -e .", "backend"),
        (688, bot, "04", "Compile", "CMake · Ninja · nvcc → build log", "backend"),
        (368, bot, "05", "Artifact and provenance", "wheel or -e · commit · flags · sha256", "store"),
        (48, bot, "06", "Verify in a fresh env", "arch list · cxx11 abi · matmul + sync", "focal"),
    ]
    # arrows first
    s += hline(272, 368, top + bh / 2, stroke=MUTED)
    s += hline(592, 688, top + bh / 2, stroke=ACCENT, marker="arrow-accent")
    s += alabel(640, top + bh / 2, "stop if absent", fill=ACCENT, gap=18, w=92)
    s += vline(800, top + bh, bot, stroke=MUTED)
    s += hline(688, 592, bot + bh / 2, stroke=MUTED)
    s += hline(368, 272, bot + bh / 2, stroke=MUTED)
    s += alabel(320, bot + bh / 2, "new shell", gap=18, w=64)
    for x, y, n, name, sub, kind in stages:
        s += node(x, y, bw, bh, name, sub, kind=kind, tagtext=n)

    s += callout(952, 348, "the deliverable is a verified artifact, not a finished build log",
                 48 + bw / 2, bot + bh + 2, colour=INK, anchor="end", leader=(944, 352),
                 cx=600, cy=356)
    return emit("12", "pytorch-build-pipeline", "A controlled PyTorch source build",
                "Pin the source and toolchain before compiling. Verify the installed "
                "result on the target device, in a clean environment.",
                "repair 2", vw, vh, s)


# ------------------------------------------------------------------ FIG 13
def fig13():
    """Prefill fills the KV cache; decode reads it and appends one token per step."""
    vw, vh = 1016, 468
    c = 20  # cell
    # --- prefill
    s = eyebrow(48, 44, "prefill · attention over the whole prompt")
    gx, gy, n = 96, 112, 6
    s += mono(gx + n * c / 2, gy - 12, "keys · prompt tokens", size=8, fill=SOFT, track="0.06em")
    s += mono(gx - 12, gy + n * c / 2 + 3, "queries", size=8, fill=SOFT, anchor="end", track="0.06em")
    for r in range(n):
        for k in range(n):
            on = k <= r
            s += (f'<rect x="{gx + k * c}" y="{gy + r * c}" width="{c}" height="{c}" '
                  f'fill="{"rgba(45,49,66,0.16)" if on else "#ffffff"}" '
                  f'stroke="rgba(45,49,66,0.28)" stroke-width="0.8"/>')
    s += mono(gx + n * c / 2, gy + n * c + 18, "T_q = T_kv = 6 · causal mask", size=8, fill=SOFT)

    # --- cache
    kx, ky, kw, kh = 336, 88, 144, 224
    s += box(kx, ky, kw, kh, fill="rgba(45,49,66,0.05)", stroke=MUTED)
    s += tag(kx + 8, ky + 6, "store", stroke=MUTED)
    s += txt(kx + kw / 2, ky + 40, "KV cache", size=12, weight="600", fill=INK)
    for i in range(4):
        s += (f'<rect x="{kx + 16}" y="{ky + 56 + i * 28}" width="{kw - 32}" height="20" rx="3" '
              f'fill="#ffffff" stroke="{MUTED}" stroke-width="0.8"/>')
        s += mono(kx + kw / 2, ky + 56 + i * 28 + 14, f"block {i}", size=8, fill=MUTED)
    s += (f'<rect x="{kx + 16}" y="{ky + 168}" width="{kw - 32}" height="20" rx="3" '
          f'fill="none" stroke="{SOFT}" stroke-width="0.8" stroke-dasharray="3,3"/>')
    s += mono(kx + kw / 2, ky + 182, "next block", size=8, fill=SOFT)
    s += mono(kx + kw / 2, ky + kh - 10, "paged · per layer", size=8, fill=SOFT)

    # --- decode
    s += eyebrow(544, 44, "decode · one query token per step")
    dx0 = 544
    for i, (step, ykv) in enumerate([("t+1", 7), ("t+2", 8), ("t+3", 9)]):
        y = 104 + i * 64
        s += mono(dx0, y + c / 2 + 3, step, size=9, fill=INK, anchor="start", weight="500")
        # query: one cell
        s += (f'<rect x="{dx0 + 40}" y="{y}" width="{c}" height="{c}" fill="rgba(79,93,117,0.10)" '
              f'stroke="{SOFT}" stroke-width="0.8"/>')
        s += mono(dx0 + 50, y + 34, "Q", size=8, fill=SOFT)
        # keys/values: prompt + generated so far
        for k in range(ykv):
            new = k == ykv - 1
            s += (f'<rect x="{dx0 + 88 + k * c}" y="{y}" width="{c}" height="{c}" '
                  f'fill="{ACCENT_TINT if new else "rgba(45,49,66,0.16)"}" '
                  f'stroke="{ACCENT if new else "rgba(45,49,66,0.28)"}" stroke-width="{1 if new else 0.8}"/>')
        s += mono(dx0 + 88 + ykv * c + 12, y + c / 2 + 3, f"T_kv = {ykv}", size=8, fill=MUTED, anchor="start")
        if i == 0:
            s += mono(dx0 + 88 + 3 * c, y + 34, "K, V · prompt + generated", size=8, fill=SOFT)

    # --- arrows
    s += hline(gx + n * c + 8, kx, 172, stroke=MUTED)
    s += alabel((gx + n * c + 8 + kx) / 2, 172, "write K,V", gap=18, w=64)
    s += hline(kx + kw, dx0 - 8, 136, stroke=MUTED)
    s += alabel((kx + kw + dx0 - 8) / 2, 136, "read", gap=18)
    s += hline(dx0 - 8, kx + kw, 232, stroke=ACCENT, marker="arrow-accent", dash="4,3")
    s += alabel((kx + kw + dx0 - 8) / 2, 232, "append", fill=ACCENT, gap=18)

    # --- capacity strip
    fy = 344
    s += f'<line x1="32" y1="{fy}" x2="{vw - 32}" y2="{fy}" stroke="{RULE}" stroke-width="0.8"/>'
    s += eyebrow(32, fy + 20, "resident kv", fill=SOFT)
    s += mono(128, fy + 21, "M_KV ≈ 2 · L · T_kv · H_kv · D · b · S", size=11, fill=INK,
              anchor="start", weight="500")
    s += mono(128, fy + 42, "= 2 · 32 layers · 4096 tokens · 8 KV heads · 128 · 2 B · 16 sequences  =  8 GiB",
              size=9, fill=MUTED, anchor="start")
    s += txt(128, fy + 62, "before weights, activations, workspaces, and allocator headroom",
             size=11, fill=SOFT, anchor="start")
    s += legend(fy + 88, vw, [("cached K, V", MUTED, "box"), ("appended this step", ACCENT, "box"),
                              ("query", SOFT, "box")])
    return emit("13", "transformer-kv-cache", "Transformer inference keeps state",
                "Prefill creates the cache; each decode step reuses it and extends it by one "
                "token, so memory grows with layers, sequences, and retained tokens.",
                "the model layer", vw, vh, s)


# ------------------------------------------------------------------ FIG 14
def fig14():
    """Four independent gates between a checkpoint and a served request."""
    vw, vh = 1016, 340
    s = eyebrow(32, 44, "what a compiled kernel does and does not unlock")

    gw, gh, gy = 152, 88, 96
    ay = gy + gh / 2
    s += node(48, gy + 8, 128, 72, "HF checkpoint", "config.json · weights", kind="input")
    gates = [
        (216, "gate 1", "CUDA execution", "a code image for this SM", "no kernel image", True),
        (400, "gate 2", "Model adapter", "listed model class", "unknown model_type", False),
        (584, "gate 3", "Feature and precision", "dtype + feature combo", "fp8 cache · chunked prefill", False),
        (768, "gate 4", "Memory and shapes", "weights + KV cache fit", "OOM at concurrency 16", False),
    ]
    # arrows
    s += hline(176, 216, ay, stroke=MUTED)
    for x, *_ in gates[1:]:
        s += hline(x - 32, x, ay, stroke=MUTED)
    s += hline(920, 968, ay, stroke=MUTED)
    s += alabel(944, ay, "serve", gap=18)
    for x, t, name, opened, blocked, focal in gates:
        s += node(x, gy, gw, gh, name, opened, kind="focal" if focal else "backend", tagtext=t)
        s += mono(x + gw / 2, gy + gh + 22, "blocked by", size=7, fill=SOFT, track="0.14em")
        s += mono(x + gw / 2, gy + gh + 36, blocked, size=8, fill=MUTED)
    s += hbracket(216, 368, gy + gh + 72, "a recompile can open this", colour=ACCENT)
    s += hbracket(400, 920, gy + gh + 72, "cannot be compiled into existence", colour=MUTED)
    return emit("14", "model-support-gates", "A compiled kernel is only the first gate",
                "Model support, features, precision, and memory are independent of "
                "architecture targets.",
                "serving", vw, vh, s)


# ------------------------------------------------------------------ FIG 15
def fig15():
    """The deployment fork: TensorRT-LLM direct, or ONNX as a sibling branch."""
    vw, vh = 1016, 420
    s = eyebrow(32, 44, "choose the runtime first, then the interchange path")

    s += node(48, 176, 176, 64, "Hugging Face checkpoint", "immutable revision", kind="input")
    # branch A
    s += node(352, 72, 208, 72, "TensorRT-LLM 1.2", "PyTorch backend · loads HF directly",
              kind="focal", tagtext="branch a")
    s += node(640, 72, 208, 72, "LLM API · trtllm-serve", "OpenAI-compatible HTTP", kind="backend")
    # branch B
    s += node(352, 264, 208, 72, "torch.onnx.export", "dynamo=True · dynamic_shapes",
              kind="backend", tagtext="branch b")
    s += node(640, 264, 208, 72, "ONNX graph", "opset · checker · shape inference", kind="store")
    s += node(872, 208, 120, 56, "TensorRT", "GPU-specific engine", kind="external")
    s += node(872, 320, 120, 56, "ONNX Runtime", "EP: TRT → CUDA → CPU", kind="external")
    # legacy path — removed
    lc, lw = chip(352, 188, "convert_checkpoint.py → trtllm-build → engine", colour=SOFT, size=8)
    s += lc
    s += f'<line x1="348" y1="196" x2="{352 + lw + 4}" y2="196" stroke="{INK}" stroke-width="1"/>'
    s += mono(352 + lw + 16, 199, "removed in 1.2", size=8, fill=SOFT, anchor="start", track="0.06em")

    # arrows
    s += elbow_hvh(224, 197, 288, 108, 352, stroke=MUTED)
    s += elbow_hvh(224, 219, 288, 300, 352, stroke=MUTED)
    s += masked(300, 96, "llm serving", size=8, fill=SOFT, anchor="start")
    s += masked(300, 316, "interchange", size=8, fill=SOFT, anchor="start")
    s += hline(560, 640, 108, stroke=MUTED)
    s += hline(560, 640, 300, stroke=MUTED)
    s += elbow_hvh(848, 288, 860, 236, 872, stroke=MUTED)
    s += elbow_hvh(848, 312, 860, 348, 872, stroke=MUTED)

    s += callout(48, 404, "ONNX is a sibling branch, not a stage before TensorRT-LLM",
                 288 + 2, 262, colour=INK, anchor="start", leader=(56, 384), cx=160, cy=372)
    return emit("15", "deployment-fork", "ONNX is a branch, not a TensorRT-LLM stage",
                "TensorRT-LLM 1.2 loads supported checkpoints through its PyTorch backend. "
                "ONNX feeds generic TensorRT or ONNX Runtime.",
                "deployment", vw, vh, s)


# ------------------------------------------------------------------ FIG 16
def fig16():
    """2x2 scenario matrix: official validation vs observed execution."""
    vw, vh = 1016, 536
    s = eyebrow(32, 44, "how to report an unlisted-hardware run")

    cx0, cy0 = 508, 276
    cw, ch, gap = 320, 128, 32
    # axes (double-ended: two outward halves so both heads point out)
    for x2 in (120, 896):
        s += f'<line x1="{cx0}" y1="{cy0}" x2="{x2}" y2="{cy0}" stroke="{INK}" stroke-width="1.2" marker-end="url(#arrow)"/>'
    for y2 in (84, 468):
        s += f'<line x1="{cx0}" y1="{cy0}" x2="{cx0}" y2="{y2}" stroke="{INK}" stroke-width="1.2" marker-end="url(#arrow)"/>'
    s += mono(cx0, 72, "listed", size=9, fill=INK, track="0.18em")
    s += mono(cx0, 488, "unlisted", size=9, fill=INK, track="0.18em")
    s += mono(108, cy0 + 3, "failed", size=9, fill=INK, anchor="end", track="0.18em")
    s += mono(908, cy0 + 3, "ran", size=9, fill=INK, anchor="start", track="0.18em")

    cells = [
        (cx0 - gap - cw, cy0 - gap - ch, "01 · listed / failed", "Regression or misconfiguration",
         ["the vendor validated this tuple —", "report it with the full audit packet"], False),
        (cx0 + gap, cy0 - gap - ch, "02 · listed / ran", "Documented configuration",
         ["what the 1.2 hardware page promises;", "still record digest, revision, precision"], False),
        (cx0 - gap - cw, cy0 + gap, "03 · unlisted / failed", "Observed failure",
         ["preserve the first relevant error;", "never rewrite it as 'T4 cannot run inference'"], False),
        (cx0 + gap, cy0 + gap, "04 · unlisted / ran", "Observed working",
         ["exact container digest, model revision,", "precision, shapes — and which path ran"], True),
    ]
    for x, y, t, name, desc, focal in cells:
        s += box(x, y, cw, ch, fill=ACCENT_TINT if focal else "rgba(45,49,66,0.04)",
                 stroke=ACCENT if focal else "rgba(79,93,117,0.28)", sw=1.2 if focal else 1)
        s += mono(x + 16, y + 22, t, size=8, fill=ACCENT if focal else MUTED, anchor="start",
                  track="0.18em", weight="600" if focal else "400")
        s += txt(x + 16, y + 52, name, size=16, weight="600", fill=INK, anchor="start")
        for j, line in enumerate(desc):
            s += txt(x + 16, y + 76 + j * 16, line, size=11, fill=MUTED, anchor="start")
        if focal:
            c1, w1 = chip(x + 16, y + 100, "ran with fallback", colour=ACCENT, fill="#ffffff")
            c2, _ = chip(x + 16 + w1 + 8, y + 100, "ran an optimized path", colour=ACCENT, fill="#ffffff")
            s += c1 + c2

    s += legend(520, vw, [("the T4 field report lands here", ACCENT, "box"),
                          ("the other three observations", MUTED, "box")])
    return emit("16", "validation-vs-execution", "Runs and supported answer different questions",
                "Official validation on one axis, observed execution on the other. Never "
                "promote one cell into another.",
                "reporting", vw, vh, s)


# ------------------------------------------------------------------ FIG 17
def fig17():
    """Only the KV term scales with admitted concurrency."""
    vw, vh = 1016, 490
    s = eyebrow(32, 44, "hypothetical config · L=32 · H_kv=8 · D=128 · T_kv=4096 · b=2 bytes")

    # ---------- the capacity test, as terms
    s += eyebrow(32, 88, "capacity test", fill=SOFT)
    x = 140
    terms = [("M_weights", False), ("M_KV", True), ("M_activations", False),
             ("M_workspaces", False), ("M_runtime", False)]
    for i, (name, focal) in enumerate(terms):
        svg, w = chip(x, 76, name, colour=ACCENT if focal else MUTED,
                      fill=ACCENT_TINT if focal else PAPER)
        s += svg
        if focal:
            s += mono(x + w / 2, 70, "scales with S", size=7, fill=ACCENT, track="0.10em")
        x += w
        if i < len(terms) - 1:
            s += mono(x + 9, 88, "+", size=10, fill=SOFT)
            x += 18
    s += mono(x + 14, 88, "<", size=11, fill=INK, weight="600")
    svg, w = chip(x + 28, 76, "M_usable GPU", colour=INK)
    s += svg
    s += mono(x + 28 + w / 2, 70, "measured after init", size=7, fill=SOFT, track="0.10em")
    s += f'<line x1="32" y1="118" x2="{vw - 32}" y2="118" stroke="{RULE}" stroke-width="0.8"/>'

    # ---------- the bars
    x0, span, gmax = 244, 684, 10.0          # 0 .. 10 GiB
    per = span / gmax
    s += eyebrow(32, 148, "resident kv values")
    s += mono(x0, 148, "M_KV  =  2 L T_kv H_kv D b S  =  0.5 GiB x S",
              size=9, fill=MUTED, anchor="start", track="0.04em")

    head = 6.0                                # KV headroom left by the fixed terms
    hx = x0 + head * per
    base, rh, gap = 180, 44, 26
    rows = [(1, 0.5, True), (4, 2.0, True), (16, 8.0, False)]

    # axis
    axis_y = base + len(rows) * (rh + gap) - gap + 18
    s += hline(x0, x0 + span + 16, axis_y, stroke=RULE_SOLID, marker="arrow")
    for g in range(0, int(gmax) + 1, 2):
        gx = x0 + g * per
        s += f'<line x1="{gx}" y1="{axis_y}" x2="{gx}" y2="{axis_y + 5}" stroke="{RULE_SOLID}" stroke-width="0.8"/>'
        s += mono(gx, axis_y + 18, str(g), size=8, fill=SOFT)
    s += mono(x0 + span + 26, axis_y + 18, "GiB", size=8, fill=SOFT, anchor="start")

    # headroom line
    s += f'<line x1="{hx}" y1="{base - 22}" x2="{hx}" y2="{axis_y}" stroke="{INK}" stroke-width="1" stroke-dasharray="4,3"/>'
    s += masked(hx, base - 28, "kv headroom left by the fixed terms", size=8, fill=INK)
    s += (f'<rect x="{hx}" y="{base - 12}" width="{x0 + span - hx}" height="{axis_y - base + 12}" '
          f'fill="{ACCENT}" fill-opacity="0.05"/>')

    for i, (S, gib, ok) in enumerate(rows):
        y = base + i * (rh + gap)
        bw = gib * per
        s += txt(x0 - 20, y + rh / 2 + 4, f"S = {S}", size=12, weight="600",
                 fill=INK if ok else ACCENT, anchor="end")
        s += mono(x0 - 20, y + rh / 2 + 18, "sequences", size=7, fill=SOFT,
                  anchor="end", track="0.10em")
        s += f'<rect x="{x0}" y="{y}" width="{span}" height="{rh}" rx="3" fill="#ffffff" stroke="{RULE}" stroke-width="0.8"/>'
        s += (f'<rect x="{x0}" y="{y}" width="{bw}" height="{rh}" rx="3" '
              f'fill="{ACCENT if not ok else "rgba(45,49,66,0.16)"}" '
              f'fill-opacity="{0.9 if not ok else 1}" stroke="{ACCENT if not ok else MUTED}" stroke-width="1"/>')
        label = f"{gib:g} GiB"
        if bw > 70:
            s += mono(x0 + bw - 12, y + rh / 2 + 3, label, size=10,
                      fill="#ffffff" if not ok else INK, anchor="end", weight="500")
        else:
            s += mono(x0 + bw + 12, y + rh / 2 + 3, label, size=10, fill=INK, anchor="start")
        s += mark(x0 + span + 34, y + rh / 2, ok, colour=MUTED if ok else ACCENT, size=11)

    s += txt(x0, axis_y + 48, "same weights, same model, same kernels \u2014 only the number of "
             "admitted sequences changed", size=14, fill=ACCENT, family=SERIF,
             anchor="start", style="italic")
    s += legend(vh - 28, vw, [("fits the headroom", MUTED, "box"),
                              ("exceeds it — admission fails, not the kernel", ACCENT, "box")])
    return emit("17", "kv-memory-budget", "Only the cache scales with concurrency",
                "The fixed terms do not move when a server admits more requests. The KV cache "
                "grows linearly with them, so capacity fails where a single request succeeded.",
                "capacity", vw, vh, s)


# ------------------------------------------------------------------ FIG 18
def fig18():
    """One request on a timeline, and why throughput is a different measurement."""
    vw, vh = 1016, 452
    s = eyebrow(32, 44, "one streamed request · not to scale")

    y = 208
    s += hline(48, 968, y, stroke=RULE_SOLID, marker="arrow")
    t0, tq, tf = 96, 208, 352
    toks = [352, 416, 480, 544]
    last = 832
    # spans on the baseline
    s += f'<rect x="{tq}" y="{y - 5}" width="{tf - tq}" height="10" rx="2" fill="rgba(45,49,66,0.16)"/>'
    s += masked(tq + (tf - tq) / 2, y + 24, "prefill", size=8, fill=MUTED)
    s += f'<rect x="{t0}" y="{y - 5}" width="{tq - t0}" height="10" rx="2" fill="rgba(45,49,66,0.06)"/>'
    s += masked(t0 + (tq - t0) / 2, y + 24, "queue", size=8, fill=SOFT)
    # events
    s += f'<circle cx="{t0}" cy="{y}" r="4" fill="{INK}"/>'
    s += masked(t0, y + 44, "request sent", size=8, fill=INK)
    for i, x in enumerate(toks):
        s += f'<circle cx="{x}" cy="{y}" r="{6 if i == 0 else 4}" fill="{ACCENT if i == 0 else INK}"/>'
    s += masked(tf, y + 44, "first token", size=8, fill=ACCENT)
    s += masked(480, y + 44, "decode steps", size=8, fill=MUTED)
    s += mono(700, y + 4, "· · ·", size=12, fill=SOFT)
    s += f'<circle cx="{last}" cy="{y}" r="6" fill="{INK}"/>'
    s += masked(last, y + 44, "last token", size=8, fill=INK)
    # brackets above
    s += hbracket(t0, tf, 152, "time to first token", colour=ACCENT, below=False, gap=14)
    s += hbracket(t0, last, 104, "end-to-end latency", colour=MUTED, below=False, gap=14)
    # inter-token gaps below
    for a, b in zip(toks, toks[1:]):
        s += f'<path d="M {a + 6} {y + 62} V {y + 68} H {b - 6} V {y + 62}" fill="none" stroke="{MUTED}" stroke-width="1"/>'
    s += mono(448, y + 86, "inter-token latency · one gap per generated token", size=8, fill=MUTED, track="0.06em")

    # throughput lane
    ty = 340
    s += f'<line x1="32" y1="{ty - 24}" x2="{vw - 32}" y2="{ty - 24}" stroke="{RULE}" stroke-width="0.8"/>'
    s += eyebrow(32, ty - 4, "throughput · aggregate over concurrent requests")
    bars = [(96, 480), (192, 640), (304, 736)]
    for i, (a, b) in enumerate(bars):
        yy = ty + 12 + i * 20
        s += f'<rect x="{a}" y="{yy}" width="{b - a}" height="12" rx="2" fill="rgba(45,49,66,0.10)" stroke="{RULE_SOLID}" stroke-width="0.8"/>'
        for x in range(a + 40, b - 8, 32):
            s += f'<line x1="{x}" y1="{yy + 2}" x2="{x}" y2="{yy + 10}" stroke="{MUTED}" stroke-width="1"/>'
        s += mono(a - 12, yy + 10, f"req {i + 1}", size=8, fill=SOFT, anchor="end")
    s += mono(760, ty + 24, "tokens per second across all requests", size=8, fill=MUTED, anchor="start")
    s += txt(760, ty + 44, "one number — it hides the latency distribution", size=11, fill=SOFT, anchor="start")
    return emit("18", "benchmark-timeline", "One request, several performance metrics",
                "TTFT ends at the first streamed token; inter-token latency describes the gaps; "
                "end-to-end ends at completion. Throughput is a different measurement.",
                "benchmark", vw, vh, s)


FIGS = {"09": fig09, "10": fig10, "11": fig11, "12": fig12, "13": fig13,
        "14": fig14, "15": fig15, "16": fig16, "17": fig17, "18": fig18}

if __name__ == "__main__":
    want = sys.argv[1:] or sorted(FIGS)
    for k in want:
        if k in FIGS:
            FIGS[k]()
