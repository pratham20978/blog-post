#!/usr/bin/env python3
"""Figures 01-08 for architecture-aware-tensorrt-llm-cuda-onnx."""
import sys

from _build import (ACCENT, ACCENT_TINT, INK, LINK, MONO, MUTED, PAPER, PAPER2, RULE,
                    RULE_SOLID, SANS, SOFT, alabel, box, callout, chip, diamond, elbow,
                    elbow_hvh, elbow_vh, emit, eyebrow, hbracket, hline, legend, mark,
                    masked, mono, node, oval, tag, txt, vbracket, vhv, vline)


# ------------------------------------------------------------------ FIG 01
def fig01():
    """Layer stack: six layers, the observation that proves each, and how little
    `is_available()` actually certifies."""
    vw, vh = 1016, 480
    s = eyebrow(128, 44, "layer")
    s += eyebrow(704, 44, "authoritative observation", anchor="end")

    x, w, h, y0 = 128, 576, 56, 64
    layers = [  # top → bottom
        ("L6", "Model and workload", "release model table · feature matrix · request log"),
        ("L5", "Serving runtime", "server log · selected kernels · fallback messages"),
        ("L4", "Framework and extensions", "get_arch_list() · warning · synchronized op"),
        ("L3", "Executable code images", "cubin sm_NN · PTX compute_NN · __CUDA_ARCH__"),
        ("L2", "Toolkit and compiler", "nvcc --list-gpu-code · resolved CMake cache"),
        ("L1", "Host, driver, GPU", "uname -m · nvidia-smi · compute_cap · UUID"),
    ]
    s += f'<rect x="{x}" y="{y0}" width="{w}" height="{h * 6}" rx="4" fill="#ffffff" stroke="{INK}" stroke-width="1"/>'
    for i, (idx, name, ev) in enumerate(layers):
        y = y0 + i * h
        if i % 2 == 1:
            s += f'<rect x="{x + 1}" y="{y}" width="{w - 2}" height="{h}" fill="{PAPER2}" fill-opacity="0.55"/>'
        if i:
            s += f'<line x1="{x}" y1="{y}" x2="{x + w}" y2="{y}" stroke="{RULE}" stroke-width="1"/>'
        s += mono(x + 20, y + h / 2 + 3, idx, size=9, fill=SOFT, anchor="start", track="0.10em")
        s += txt(x + 64, y + h / 2 + 5, name, size=14, weight="600", fill=INK, anchor="start")
        s += mono(x + w - 16, y + h / 2 + 3, ev, size=9, fill=MUTED, anchor="end")

    # direction indicator — audit bottom-up
    ax = 88
    s += vline(ax, y0 + h * 6 - 8, y0 + 12, stroke=MUTED, marker="arrow")
    s += mono(ax, y0 + h * 6 + 20, "audit", size=8, fill=SOFT, track="0.14em")
    s += mono(ax, y0 + h * 6 + 32, "upward", size=8, fill=SOFT, track="0.14em")

    # what one green light proves
    bx = 732
    s += vbracket(bx, y0 + 5 * h + 4, y0 + 6 * h - 4, "is_available()", colour=ACCENT)
    s += vbracket(bx, y0 + 4, y0 + 5 * h - 4, "still unproven", colour=SOFT)
    s += callout(1000, 440, "the weakest green light in the stack",
                 bx + 2, y0 + 6 * h - 2, colour=ACCENT, anchor="end",
                 leader=(988, 446), cx=880, cy=450)
    s += txt(1000, 458, "it proves a driver and a device, nothing above them",
             size=11, fill=SOFT, anchor="end")

    return emit("01", "compatibility-stack", "Compatibility is a stack",
                "Each layer needs its own observation. A pass at one layer cannot "
                "certify the layers above it.",
                "the stack", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    """Two ordinal axes that are often compared as if they were one number."""
    vw, vh = 1016, 452
    s = eyebrow(32, 44, "two numbers that look alike")

    # --- top axis: compute capability (hardware)
    ya = 140
    caps = [("sm_75", "7.5", "T4"), ("sm_80", "8.0", None), ("sm_86", "8.6", None),
            ("sm_89", "8.9", None), ("sm_90", "9.0", None), ("sm_100", "10.0", None),
            ("sm_120", "12.0", None), ("sm_121", "12.1", "GB10")]
    xs = [128 + i * 108 for i in range(8)]
    s += hline(96, 936, ya, stroke=RULE_SOLID, marker="arrow")
    s += eyebrow(128, 100, "gpu compute capability — a hardware feature level")
    for x, (code, num, prod) in zip(xs, caps):
        focal = code == "sm_121"
        s += f'<circle cx="{x}" cy="{ya}" r="{5 if prod else 4}" fill="{ACCENT if focal else (INK if prod else MUTED)}"/>'
        s += mono(x, ya - 14, code, size=9, fill=ACCENT if focal else MUTED, track="0.04em")
        s += mono(x, ya + 20, num, size=8, fill=ACCENT if focal else SOFT)
        if prod:
            s += txt(x, ya + 36, prod, size=11, weight="600", fill=INK)

    # --- compiler in the middle: the only relation that matters
    bx, by, bw, bh = 400, 224, 216, 44
    s += node(bx, by, bw, bh, "selected nvcc", "nvcc --list-gpu-code", kind="backend")
    s += vhv(bx + bw / 3, by, xs[0], ya + 48, 200, stroke=MUTED, dash="4,3")
    s += vhv(bx + 2 * bw / 3, by, xs[7], ya + 48, 200, stroke=MUTED, dash="4,3")
    s += masked(300, 196, "still emits sm_75", size=8, fill=SOFT)
    s += masked(716, 196, "lists sm_121", size=8, fill=SOFT)

    # --- bottom axis: toolkit release (software)
    yb = 332
    tks = ["11.8", "12.0", "12.1", "12.4", "12.8", "13.0", "13.1"]
    xt = [128 + i * 124 for i in range(7)]
    s += hline(96, 936, yb, stroke=RULE_SOLID, marker="arrow")
    for x, v in zip(xt, tks):
        trap = v == "12.1"
        sel = v == "13.1"
        s += f'<circle cx="{x}" cy="{yb}" r="{5 if sel else 4}" fill="{ACCENT if trap else (INK if sel else MUTED)}"/>'
        s += mono(x, yb + 20, v, size=8, fill=ACCENT if trap else (INK if sel else SOFT))
    s += eyebrow(128, 376, "cuda toolkit release — a software version")
    s += vhv(xt[6], yb - 6, bx + bw / 2, by + bh, 300, stroke=MUTED)
    s += masked(xt[6] + 12, 314, "selected on PATH", size=8, fill=SOFT, anchor="start")

    # --- the trap
    s += callout(1000, 420, "same digits, different axis — 12.1 here is not sm_121",
                 xt[2] + 12, yb + 22, colour=INK, anchor="end", leader=(992, 424),
                 cx=700, cy=432)
    return emit("02", "capability-vs-toolkit", "Compute capability is not a CUDA release",
                "The selected compiler must list the target. The two numbers never need to match.",
                "hardware vs software", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    """Same symptom, opposite lifecycle: two case cards with the failing row lit."""
    vw, vh = 1016, 472
    s = eyebrow(32, 44, "one error string, two case files")

    # shared symptom
    sx, sy, sw, sh = 296, 60, 424, 44
    s += box(sx, sy, sw, sh, fill="rgba(45,49,66,0.05)", stroke=MUTED)
    s += tag(sx + 8, sy + 6, "symptom", stroke=MUTED)
    s += mono(sx + sw / 2 + 24, sy + sh / 2 + 3, "no kernel image is available for execution",
              size=9, fill=INK, weight="500")

    cards = [
        (64, "Machine A", "NVIDIA T4", "sm_75", "hardware older than the release",
         [("device visible", "nvidia-smi · 7.5", True),
          ("compiler lists target", "nvcc lists sm_75", True),
          ("artifact has a code image", "older stack · unfused fallback", True),
          ("release validated", "not on the 1.2 hardware page", False)],
         "product validation", "pin a known tuple, or report an unlisted-hardware run"),
        (528, "Machine B", "GB10-class", "sm_121", "binary older than the hardware",
         [("device visible", "nvidia-smi · 12.1", True),
          ("compiler lists target", "nvcc lists sm_121", True),
          ("artifact has a code image", "pinned wheel: no 12.x image", False),
          ("release validated", "not the failing layer", None)],
         "binary inventory", "replace the wheel; build PyTorch only if none covers 12.x"),
    ]
    cy0, cw, ch = 144, 424, 288
    for cx, name, prod, sm, life, rows, gap, repair in cards:
        s += box(cx, cy0, cw, ch, fill="#ffffff", stroke=INK)
        # header
        s += txt(cx + 16, cy0 + 30, name, size=14, weight="600", fill=INK, anchor="start")
        s += mono(cx + 16, cy0 + 48, f"{prod} · {sm}", size=9, fill=MUTED, anchor="start")
        s += mono(cx + cw - 16, cy0 + 30, life, size=8, fill=SOFT, anchor="end", track="0.06em")
        s += f'<line x1="{cx}" y1="{cy0 + 64}" x2="{cx + cw}" y2="{cy0 + 64}" stroke="{RULE}" stroke-width="1"/>'
        # rows
        ry, rh = cy0 + 64, 40
        for i, (label, ev, ok) in enumerate(rows):
            y = ry + i * rh
            if ok is False:
                s += f'<rect x="{cx + 1}" y="{y}" width="{cw - 2}" height="{rh}" fill="{ACCENT_TINT}"/>'
            if i:
                s += f'<line x1="{cx}" y1="{y}" x2="{cx + cw}" y2="{y}" stroke="{RULE}" stroke-width="1"/>'
            s += txt(cx + 40, y + rh / 2 + 4, label, size=12, weight="500",
                     fill=ACCENT if ok is False else INK, anchor="start")
            s += mono(cx + cw - 16, y + rh / 2 + 3, ev, size=9,
                      fill=ACCENT if ok is False else SOFT, anchor="end")
            if ok is None:
                s += f'<line x1="{cx + 16}" y1="{y + rh / 2}" x2="{cx + 26}" y2="{y + rh / 2}" stroke="{SOFT}" stroke-width="1.4"/>'
            else:
                s += mark(cx + 21, y + rh / 2, ok)
        # verdict
        vy = ry + 4 * rh
        s += f'<line x1="{cx}" y1="{vy}" x2="{cx + cw}" y2="{vy}" stroke="{INK}" stroke-width="1"/>'
        s += eyebrow(cx + 16, vy + 24, "gap", fill=SOFT)
        s += txt(cx + 72, vy + 25, gap, size=12, weight="600", fill=INK, anchor="start")
        s += eyebrow(cx + 16, vy + 52, "repair", fill=SOFT)
        s += txt(cx + 72, vy + 53, repair, size=11, fill=MUTED, anchor="start")

    # symptom → cards
    s += vhv(sx + sw / 3, sy + sh, 64 + cw / 2, cy0, 124, stroke=MUTED)
    s += vhv(sx + 2 * sw / 3, sy + sh, 528 + cw / 2, cy0, 124, stroke=MUTED)

    return emit("03", "two-hosts", "Same symptom, opposite lifecycle",
                "The T4 case is a product-validation question. The sm_121 case is a "
                "binary-inventory question. Similar errors do not imply the same rebuild.",
                "case files", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    """Flowchart: how the driver picks something it can execute from a fatbinary."""
    vw, vh = 1016, 500
    s = eyebrow(32, 44, "what happens at the first kernel launch")

    # inventory
    fx, fy, fw, fh = 48, 80, 232, 240
    s += box(fx, fy, fw, fh, fill="rgba(45,49,66,0.05)", stroke=MUTED)
    s += tag(fx + 8, fy + 6, "inventory", stroke=MUTED)
    s += txt(fx + 16, fy + 40, "fatbinary", size=12, weight="600", fill=INK, anchor="start")
    s += mono(fx + 16, fy + 56, "inside one .so", size=8, fill=SOFT, anchor="start")
    items = [("sm_75 cubin", INK), ("sm_80 cubin", INK), ("sm_90 cubin", INK),
             ("sm_120 cubin", INK), ("compute_120 PTX", MUTED)]
    for i, (t, c) in enumerate(items):
        c_svg, _ = chip(fx + 16, fy + 72 + i * 28, t, colour=c, fill="#ffffff")
        s += c_svg
    s += mono(fx + 16, fy + fh - 14, "no sm_121 image — but is one needed?", size=8,
              fill=SOFT, anchor="start")

    # decisions
    dx, dw, dh = 496, 224, 80
    ds = [(120, "exact cubin for this SM?", "sm_121"),
          (240, "compatible cubin?", "baseline or family · sm_120"),
          (360, "PTX the driver can JIT?", "embedded PTX ≤ driver version")]
    outs = [(96, "Run the native image", "direct load", "backend"),
            (216, "Run compatible code", "may lack native optimizations", "backend"),
            (336, "JIT-compile, then run", "slow first launch · cached after", "backend")]
    # arrows first
    s += hline(fx + fw, dx - dw / 2, 120, stroke=MUTED)
    s += alabel(388, 120, "lookup", gap=18)
    for i, (cy, _, _) in enumerate(ds):
        s += hline(dx + dw / 2, 712, cy, stroke=MUTED)
        s += alabel(660, cy, "yes", gap=18)
        if i < 2:
            s += vline(dx, cy + dh / 2, ds[i + 1][0] - dh / 2, stroke=MUTED)
            s += masked(dx + 12, cy + dh / 2 + 24, "no", size=8, fill=SOFT, anchor="start")
    s += vline(dx, 360 + dh / 2, 428, stroke=ACCENT, marker="arrow-accent")
    s += masked(dx + 12, 420, "no", size=8, fill=ACCENT, anchor="start")
    # nodes
    for cy, name, sub in ds:
        s += diamond(dx, cy, dw, dh, name, sub)
    for y, name, sub, kind in outs:
        s += node(712, y, 256, 48, name, sub, kind=kind)
    s += oval(368, 428, 256, 40, "no kernel image is available", stroke=ACCENT,
              fill=ACCENT_TINT, tcolor=ACCENT)

    s += callout(fx, 376, "enumeration succeeded long before this",
                 fx + 112, fy + fh + 2, colour=INK, anchor="start", leader=(fx + 8, 356),
                 cx=fx + 40, cy=336)
    return emit("04", "code-image-selection", "How the driver finds executable code",
                "Cubin first, PTX JIT when compatible, failure otherwise — and none of it "
                "runs during device enumeration.",
                "runtime selection", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    """Decision tree: five gates, each with the command that decides it and the
    repair that owns a failure."""
    vw, vh = 1016, 656
    s = eyebrow(356, 44, "decided by", anchor="end")
    s += eyebrow(712, 44, "owner of a failure")

    dx, dw, dh, step = 496, 248, 80, 104
    gates = [
        ("intended GPU visible?", "device · UUID · compute_cap",
         "nvidia-smi --query-gpu",
         "Repair assignment", "driver · container · CUDA_VISIBLE_DEVICES", False),
        ("nvcc lists the target?", "compute_NN and sm_NN",
         "nvcc --list-gpu-code",
         "Select a Toolkit", "one that knows the SM · pin CUDA_HOME", False),
        ("PyTorch core op passes?", "warning + synchronized op",
         "audit_torch.py",
         "Replace wheel, else build PyTorch", "Repair 0, then Repair 2", True),
        ("extension passes?", "same process, device, dtype",
         "test_extension.py",
         "Rebuild that extension", "TORCH_CUDA_ARCH_LIST · same ABI", False),
        ("model class and features listed?", "resolved config vs release table",
         "inspect_model.py",
         "Pin a release or change runtime", "Repair 4 · no flag restores it", False),
    ]
    cys = [104 + i * step for i in range(5)]
    # arrows
    for i, cy in enumerate(cys):
        s += hline(dx + dw / 2, 712, cy, stroke=MUTED)
        s += alabel(668, cy, "no", gap=18)
        nxt = cys[i + 1] - dh / 2 if i < 4 else 592
        s += vline(dx, cy + dh / 2, nxt, stroke=MUTED)
        s += masked(dx + 12, cy + dh / 2 + 18, "yes", size=8, fill=SOFT, anchor="start")
        s += hline(360, dx - dw / 2, cy, stroke=RULE_SOLID, marker=None)
    # nodes
    for cy, (q, sub, cmd, rep, rsub, focal) in zip(cys, gates):
        s += diamond(dx, cy, dw, dh, q, sub)
        s += mono(352, cy + 3, cmd, size=9, fill=MUTED, anchor="end")
        s += node(712, cy - 28, 256, 56, rep, rsub, kind="focal" if focal else "backend")
    s += oval(392, 592, 208, 40, "run, then measure", stroke=INK)

    s += callout(48, 596, "each pass moves the question one layer up",
                 dx - 4, cys[4] + dh / 2 + 24, colour=INK, anchor="start",
                 leader=(56, 576), cx=240, cy=556)
    return emit("05", "audit-decision-tree", "Audit before compiling",
                "Stop at the first failing layer. Rebuild only after a failing test names "
                "the artifact that owns the missing kernel.",
                "audit order", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    """The decisive PyTorch test: inventory + compatibility rule + real launch."""
    vw, vh = 1016, 400
    s = eyebrow(32, 44, "what actually decides the pytorch layer")

    # inputs
    s += node(48, 88, 232, 64, "Device capability", "get_device_capability() → (12, 1)", kind="input")
    s += node(48, 184, 232, 64, "Compiled code images", "get_arch_list() → [sm_80 … sm_120]", kind="input")
    # rule
    rx, ry, rw, rh = 352, 112, 232, 96
    s += node(rx, ry, rw, rh, "Compatibility check", "torch/cuda/__init__.py", kind="backend",
              tagtext="pytorch rule")
    s += mono(rx + rw / 2, ry + rh - 10, "baseline · family · exact target", size=8, fill=SOFT)
    # op
    ox, oy, ow, oh = 656, 128, 232, 64
    s += node(ox, oy, ow, oh, "Synchronized core op", "(arange(8)+1).sum() · item()", kind="backend")
    # outcomes
    s += node(608, 264, 160, 56, "Core passes", "move up the stack", kind="backend")
    s += node(792, 264, 176, 56, "No kernel image", "PyTorch binary owns the gap", kind="focal")

    # arrows (drawn after nodes here is fine: they only touch edges)
    s += elbow_hvh(280, 120, 316, ry + rh / 3, rx, stroke=MUTED)
    s += elbow_hvh(280, 216, 316, ry + 2 * rh / 3, rx, stroke=MUTED)
    s += hline(rx + rw, ox, 160, stroke=MUTED)
    s += alabel(620, 160, "may warn", gap=18, w=64)
    s += vhv(ox + ow / 3, oy + oh, 688, 264, 228, stroke=MUTED)
    s += vhv(ox + 2 * ow / 3, oy + oh, 880, 264, 228, stroke=ACCENT, marker="arrow-accent")
    s += masked(ox + ow / 3 - 12, 218, "pass", size=8, fill=SOFT, anchor="end")
    s += masked(ox + 2 * ow / 3 + 12, 218, "fail", size=8, fill=ACCENT, anchor="start")

    # the anti-test
    ax, ay = 48, 300
    c_svg, cw = chip(ax, ay, "'sm_121' in get_arch_list()", colour=MUTED, fill="#ffffff", size=9, h=20)
    s += c_svg
    s += f'<line x1="{ax - 4}" y1="{ay + 10}" x2="{ax + cw + 4}" y2="{ay + 10}" stroke="{INK}" stroke-width="1.2"/>'
    s += mark(ax + cw + 20, ay + 10, False, colour=MUTED)
    s += txt(ax, ay + 44, "a string test is not the rule PyTorch applies",
             size=14, fill=INK, family="'Instrument Serif', Georgia, serif", anchor="start",
             style="italic")
    s += txt(ax, ay + 62, "a family or baseline image can cover a 12.1 device", size=11,
             fill=SOFT, anchor="start")
    return emit("06", "pytorch-compatibility-test", "The decisive PyTorch test",
                "Inventory, PyTorch's own compatibility logic, its warning, and a real "
                "launch — read together.",
                "layer 4", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    """nvcc pipeline: virtual PTX, real cubins, one fatbinary."""
    vw, vh = 1016, 424
    s = eyebrow(272, 44, "1 · virtual architecture")
    s += eyebrow(528, 44, "2 · real architecture")
    s += eyebrow(784, 44, "3 · one package")

    # source
    s += node(48, 176, 144, 64, "kernel.cu", "device code", kind="input", tagtext="source")
    # lanes
    lanes = [(104, "compute_75", "sm_75", "--generate-code arch=compute_75,code=sm_75"),
             (248, "compute_121", "sm_121", "--generate-code arch=compute_121,code=sm_121")]
    for y, v, r, flag in lanes:
        s += mono(272, y + 72, flag, size=8, fill=SOFT, anchor="start")
        s += node(272, y, 176, 56, v, "PTX · virtual ISA", kind="backend")
        s += node(528, y, 176, 56, r, "cubin · native code", kind="backend")
    # fatbinary
    fx, fy, fw, fh = 784, 72, 184, 240
    s += box(fx, fy, fw, fh, fill="rgba(45,49,66,0.05)", stroke=MUTED)
    s += tag(fx + 8, fy + 6, "fatbinary", stroke=MUTED)
    chips = [(124, "sm_75 cubin", INK), (196, "compute_121 PTX", MUTED), (268, "sm_121 cubin", INK)]
    for cy, t, c in chips:
        c_svg, _ = chip(fx + 16, cy - 8, t, colour=c, fill="#ffffff")
        s += c_svg
    s += mono(fx + 16, fy + fh - 12, "driver picks one at launch", size=8, fill=SOFT, anchor="start")

    # arrows
    s += elbow_hvh(192, 196, 232, 132, 272, stroke=MUTED)
    s += elbow_hvh(192, 220, 232, 276, 272, stroke=MUTED)
    for y in (132, 276):
        s += hline(448, 528, y, stroke=MUTED)
        s += alabel(488, y, "ptxas", gap=18)
        s += hline(704, 784, y, stroke=MUTED)
    s += elbow_vh(360, 248, 784, 196, stroke=MUTED, dash="4,3")
    s += masked(620, 188, "PTX kept for forward JIT", size=8, fill=SOFT)

    # notes strip
    ny = 352
    s += f'<line x1="32" y1="{ny}" x2="{vw - 32}" y2="{ny}" stroke="{RULE}" stroke-width="0.8"/>'
    s += eyebrow(32, ny + 18, "cost", fill=SOFT)
    s += txt(96, ny + 19, "every extra real target: more compile time, a bigger artifact",
             size=11, fill=MUTED, anchor="start")
    s += eyebrow(32, ny + 40, "ptx", fill=SOFT)
    s += txt(96, ny + 41, "a forward-JIT option for later GPUs — not native optimizations for them",
             size=11, fill=MUTED, anchor="start")
    return emit("07", "cuda-compilation-pipeline", "From CUDA source to executable inventory",
                "Real cubins and virtual PTX travel together in one fatbinary. The driver "
                "chooses among them at launch.",
                "nvcc", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    """CUDA_ARCHITECTURES values → what gets emitted."""
    vw, vh = 1016, 500
    s = eyebrow(64, 44, "CUDA_ARCHITECTURES value")
    s += eyebrow(560, 44, "emitted code")

    vals = [(108, "75-real"), (164, "121-real"), (228, "121-virtual"), (296, "121"), (360, "native")]
    for cy, v in vals:
        s += box(64, cy - 20, 176, 40, fill="#ffffff", stroke=INK)
        s += mono(64 + 88, cy + 4, v, size=11, fill=INK, weight="500")
    outs = [(84, "sm_75 cubin", "native · runs on T4 directly"),
            (148, "sm_121 cubin", "native · runs on GB10 directly"),
            (212, "compute_121 PTX", "virtual · driver JIT on later GPUs")]
    for y, name, sub in outs:
        s += node(560, y, 208, 48, name, sub, kind="backend")
    s += box(560, 336, 208, 48, fill="rgba(45,49,66,0.02)", stroke="rgba(45,49,66,0.30)", dash="4,3")
    s += txt(664, 356, "cubin for that host's GPU", size=12, weight="600", fill=INK)
    s += mono(664, 372, "not necessarily the fleet's", size=9, fill=SOFT)

    # connectors
    s += hline(240, 560, 108, stroke=MUTED)
    s += hline(240, 560, 164, stroke=MUTED)
    # 121-virtual crosses the vertical of the bare "121" fan → hop over it at x=400
    s += (f'<path d="M 240 228 H 392 a 8,8 0 0,1 16,0 H 560" fill="none" stroke="{MUTED}" '
          f'stroke-width="1" marker-end="url(#arrow)"/>')
    s += elbow_hvh(240, 288, 400, 180, 560, stroke=MUTED)
    s += elbow_hvh(240, 304, 432, 244, 560, stroke=MUTED)
    s += masked(300, 280, "both", size=8, fill=SOFT)
    # native → decision
    dcx, dcy = 432, 360
    s += hline(240, dcx - 88, dcy, stroke=MUTED)
    s += diamond(dcx, dcy, 176, 72, "GPU on build host?", "CMake ≥ 3.24 infers it")
    s += hline(dcx + 88, 560, dcy, stroke=MUTED)
    s += alabel(540, dcy, "yes", gap=18)
    s += vline(dcx, dcy + 36, 428, stroke=ACCENT, marker="arrow-accent")
    s += masked(dcx + 12, 420, "no", size=8, fill=ACCENT, anchor="start")
    s += oval(320, 428, 224, 40, "nothing inferred", stroke=ACCENT, fill=ACCENT_TINT, tcolor=ACCENT)
    s += mono(432, 486, "GPU-less CI · cross-builds · heterogeneous fleets", size=8, fill=SOFT)

    s += vbracket(792, 84, 260, "what the driver can load", colour=MUTED)
    s += vbracket(792, 336, 384, "only on that host", colour=SOFT)
    return emit("08", "cmake-target-map", "CMake architecture notation",
                "-real requests a cubin, -virtual requests PTX, a bare number requests both, "
                "and native asks CMake to guess from the build host.",
                "cmake", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05,
        "06": fig06, "07": fig07, "08": fig08}

if __name__ == "__main__":
    want = sys.argv[1:] or sorted(FIGS)
    for k in want:
        if k in FIGS:
            FIGS[k]()
