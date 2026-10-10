#!/usr/bin/env python3
"""Generate figures 1-8 for four-cuda-version-numbers.

    python3 _figs.py            # all figures
    python3 _figs.py 3 5        # only those numbers

Every figure emits a triplet: an editable .html, an .svg, and a 2x .png. The
.html is the handoff contract's source of truth; this file is the generator
that produced it, kept so a correction is an edit here plus a re-run.

Figure 7 is routed `mermaid` and is NOT produced here -- see _fig07.mmd and the
mermaid-cli command in manifest.md.

All strings below are real: every version, path, error code and driver number
appears in research/ledger.md with the artifact it was read from.
"""

import sys

from _build import (ACCENT, ACCENT_TINT, INK, LINK, MONO, MUTED, PAPER, RULE,
                    RULE_SOLID, SANS, SERIF, SOFT, box, callout, chip, elbow_vh,
                    emit, eyebrow, hbracket, hline, legend, mark, mono, node,
                    tag, txt, vbracket, vline)

# The four numbers, in the order the post introduces them.
W = 960


def fig01():
    """Four rows: artifact, file on disk, command, what it promises."""
    vh = 500
    s = ""
    cols = [(40, 150, "the artifact"), (360, 214, "file on disk"),
            (580, 232, "what prints it"), (736, 232, "what it promises")]
    for x, w, label in cols:
        s += eyebrow(x, 44, label, fill=SOFT)

    rows = [
        ("1", "kernel-mode driver", "nvidia.ko", "nvidia-smi → KMD",
         "which driver branch is loaded", "not a CUDA number at all", "580.65.06"),
        ("2", "CUDA user-mode driver", "libcuda.so.1", "nvidia-smi → CUDA UMD",
         "a ceiling: newest CUDA served", "never an inventory", "13.0"),
        ("3", "CUDA runtime", "libcudart.so.13", "cudaRuntimeGetVersion",
         "a constant, set at compile time", "never discovered at run time", "13.0"),
        ("4", "Toolkit compiler", "nvcc", "nvcc --version",
         "which compiler is installed", "says nothing about what runs", "13.4"),
    ]
    y = 64
    for i, (num, name, path, cmd, p1, p2, value) in enumerate(rows):
        focal = i in (1, 2)
        h = 84
        stroke = ACCENT if focal else INK
        s += box(40, y, W - 80, h, fill=ACCENT_TINT if focal else "#ffffff",
                 stroke=stroke, rx=6)
        # number badge
        s += (f'<circle cx="68" cy="{y + h / 2}" r="13" fill="none" '
              f'stroke="{stroke}" stroke-width="1"/>')
        s += txt(68, y + h / 2 + 5, num, size=13, weight="600",
                 fill=ACCENT if focal else INK)
        s += txt(92, y + 34, name, size=13, weight="600", anchor="start",
                 fill=ACCENT if focal else INK)
        s += mono(92, y + 54, f"version looks like  {value}", size=9, fill=SOFT,
                  anchor="start")

        s += vline(340, y + 12, y + h - 12, stroke=RULE_SOLID, sw=0.8, marker=None)
        s += mono(360, y + 40, path, size=11, fill=INK, anchor="start", weight="500")
        s += mono(360, y + 58, "host" if i < 2 else ("wheel" if i == 2 else "Toolkit"),
                  size=8, fill=SOFT, anchor="start", track="0.10em")

        s += vline(560, y + 12, y + h - 12, stroke=RULE_SOLID, sw=0.8, marker=None)
        s += mono(580, y + 46, cmd, size=10, fill=MUTED, anchor="start")

        # Keep the two longest command strings clear of the following divider.
        s += vline(720, y + 12, y + h - 12, stroke=RULE_SOLID, sw=0.8, marker=None)
        s += txt(736, y + 38, p1, size=10, fill=INK, anchor="start")
        s += txt(736, y + 54, p2, size=10, fill=SOFT, anchor="start")
        y += h + 10

    s += legend(vh - 24, W, [
        ("the two that decide whether a launch works", ACCENT, "box"),
        ("reported, never decisive", INK, "hollow"),
    ])
    return emit("01", "four-numbers", "The four CUDA version numbers",
                "Each number is a property of one artifact. The fourth column is "
                "the one that matters: only rows 2 and 3 take part in the decision "
                "that lets a program run.",
                "part 2 · figure 1", W, vh, s)


def fig02():
    """A command x artifact matrix: which command reports which artifact's number."""
    vh = 470
    s = eyebrow(40, 44, "which command reports which artifact's number", fill=SOFT)

    cmds = [
        ("nvidia-smi", "prints two fields at once", [0, 1], "580.65.06  \u00b7  13.0"),
        ("cat /proc/driver/nvidia/version", "procfs, no intermediary", [0], "580.65.06"),
        ("deviceQuery", "prints the pair", [1, 2], "13.0 / 13.4"),
        ("torch.version.cuda", "the build-time record", [2], "13.0"),
        ("nvcc --version", "often absent entirely", [3], "13.4"),
    ]
    arts = [
        ("nvidia.ko", "kernel module", False),
        ("libcuda.so.1", "user-mode driver", True),
        ("libcudart.so.13", "in the wheel", True),
        ("nvcc", "Toolkit", False),
    ]

    x0, colw = 430, 130
    # column headers
    for j, (name, role, focal) in enumerate(arts):
        cx = x0 + j * colw + colw / 2
        colour = ACCENT if focal else INK
        s += mono(cx, 86, name, size=9.5, fill=colour, weight="600")
        s += txt(cx, 102, role, size=8, fill=SOFT)
        s += mono(cx, 118, f"number {j + 1}", size=7.5, fill=SOFT, track="0.10em")
        if focal:
            s += (f'<rect x="{x0 + j * colw + 6}" y="128" width="{colw - 12}" '
                  f'height="{len(cmds) * 44 + 8}" rx="4" fill="{ACCENT}" '
                  f'fill-opacity="0.06"/>')

    y = 136
    for name, note, targets, value in cmds:
        s += (f'<line x1="40" y1="{y + 34}" x2="{x0 + 4 * colw}" y2="{y + 34}" '
              f'stroke="{RULE}" stroke-width="0.8"/>')
        s += mono(48, y + 18, name, size=10, fill=INK, anchor="start", weight="500")
        s += txt(48, y + 31, note, size=8.5, fill=SOFT, anchor="start")
        s += mono(414, y + 20, value, size=8.5, fill=MUTED, anchor="end")
        for j in range(4):
            cx = x0 + j * colw + colw / 2
            if j in targets:
                focal = arts[j][2]
                colour = ACCENT if focal else INK
                s += f'<circle cx="{cx}" cy="{y + 16}" r="5.5" fill="{colour}"/>'
            else:
                s += (f'<circle cx="{cx}" cy="{y + 16}" r="2" fill="none" '
                      f'stroke="{RULE_SOLID}" stroke-width="0.8"/>')
        y += 44

    # The convergence: two filled dots in column 0.
    s += (f'<rect x="{x0 + 6}" y="132" width="{colw - 12}" height="{2 * 44}" rx="4" '
          f'fill="none" stroke="{ACCENT}" stroke-width="1.2" stroke-dasharray="4 3"/>')
    s += callout(200, y + 44, "two commands, one artifact \u2014 which is why it is four numbers, not five",
                 x0 + colw / 2, y + 6, colour=ACCENT, anchor="start",
                 leader=(200, y + 30), cx=330, cy=y + 40)

    s += legend(vh - 24, W, [
        ("the two numbers the launch decision compares", ACCENT, "dot"),
        ("reported, never decisive", INK, "dot"),
    ])
    return emit("02", "five-commands", "Five commands, four artifacts",
                "Each row is one command; each column is the artifact that owns "
                "the number. Column one is filled twice, which is why the count "
                "is four rather than five.",
                "part 2 \u00b7 figure 2", W, vh, s)


def fig03():
    """A version axis with the driver ceiling and three application runtimes."""
    vh = 440
    s = eyebrow(40, 44, "one host, three applications", fill=SOFT)

    lo, hi = 12.8, 13.6
    x0, x1 = 300, 880

    def px(v):
        return x0 + (v - lo) / (hi - lo) * (x1 - x0)

    axis_y = 344
    top = 96

    # Bands by MAJOR FAMILY -- that is what actually decides, not "above/below".
    s += (f'<rect x="{px(12.8)}" y="{top}" width="{px(13.0) - px(12.8)}" '
          f'height="{axis_y - top}" fill="{INK}" fill-opacity="0.05"/>')
    s += mono(px(12.9), top + 18, "CUDA 12 family", size=8, fill=MUTED, track="0.10em")
    s += (f'<rect x="{px(13.0)}" y="{top}" width="{px(13.6) - px(13.0)}" '
          f'height="{axis_y - top}" fill="{ACCENT}" fill-opacity="0.06"/>')
    s += mono(px(13.3), top + 18, "CUDA 13 family \u2014 every point in here runs",
              size=8, fill=ACCENT, track="0.10em")

    # the ceiling
    ceil_x = px(13.0)
    s += (f'<line x1="{ceil_x}" y1="{top}" x2="{ceil_x}" y2="{axis_y}" '
          f'stroke="{ACCENT}" stroke-width="1.4"/>')
    s += mono(ceil_x, top - 26, "driver ceiling 13.0", size=10, fill=ACCENT,
              weight="500")
    s += mono(ceil_x, top - 12, "KMD 580.65.06", size=8.5, fill=SOFT)

    s += f'<line x1="{x0}" y1="{axis_y}" x2="{x1}" y2="{axis_y}" stroke="{MUTED}" stroke-width="1"/>'
    for v in (12.8, 13.0, 13.2, 13.4, 13.6):
        s += (f'<line x1="{px(v)}" y1="{axis_y}" x2="{px(v)}" y2="{axis_y + 6}" '
              f'stroke="{MUTED}" stroke-width="0.8"/>')
        s += mono(px(v), axis_y + 20, f"{v:.1f}", size=9, fill=SOFT)
    s += mono(x0 - 14, axis_y + 4, "runtime version", size=9, fill=SOFT, anchor="end")

    cases = [
        (12.9, "runtime 12.9", "older major family", False, "different major family"),
        (13.0, "runtime 13.0", "equal to the ceiling", True, "runs"),
        (13.4, "runtime 13.4", "ahead of the ceiling", True, "runs \u2014 minor version compat"),
    ]
    y = 150
    for v, label, note, ok, verdict in cases:
        s += (f'<circle cx="{px(v)}" cy="{y}" r="6" fill="{PAPER}" '
              f'stroke="{ACCENT if ok else INK}" stroke-width="1.6"/>')
        s += (f'<line x1="{px(v)}" y1="{y + 8}" x2="{px(v)}" y2="{axis_y - 2}" '
              f'stroke="{RULE_SOLID}" stroke-width="0.8" stroke-dasharray="2 3"/>')
        s += mono(40, y + 4, label, size=10, fill=INK, anchor="start", weight="500")
        s += txt(40, y + 20, note, size=9, fill=SOFT, anchor="start")
        s += mark(196, y, ok)
        s += txt(224, y + 4, verdict, size=10, fill=ACCENT if ok else INK,
                 anchor="start")
        y += 62

    s += txt(W / 2, 404, "The runtime being ahead of the ceiling is not the failure "
             "case. Leaving the major family is.",
             size=11, fill=MUTED, family=SERIF, style="italic")
    return emit("03", "ceiling-and-constant", "A ceiling, and three constants",
                "The host fixes one ceiling. Each application carries a constant. "
                "What decides the launch is the major family, not whether the "
                "runtime sits above the ceiling.",
                "part 2 \u00b7 figure 3", W, vh, s)


def fig04():
    """Driver-number axis with the three major-family floors, drawn to scale."""
    vh = 430
    s = eyebrow(40, 44, "minimum driver, by major family", fill=SOFT)

    lo, hi = 430, 640
    x0, x1 = 150, 900

    def px(v):
        return x0 + (v - lo) / (hi - lo) * (x1 - x0)

    bands = [
        ("CUDA 11.x", 450, 525, "driver \u2265 450", "< 525", INK),
        ("CUDA 12.x", 525, 580, "driver \u2265 525", "< 580", INK),
        ("CUDA 13.x", 580, 640, "driver \u2265 580", "no upper bound", ACCENT),
    ]
    y = 84
    for label, start_v, end_v, note, cap, colour in bands:
        h = 50
        s += (f'<rect x="{px(start_v)}" y="{y}" width="{px(end_v) - px(start_v)}" '
              f'height="{h}" rx="4" fill="{colour}" fill-opacity="0.08" '
              f'stroke="{colour}" stroke-width="1"/>')
        s += txt(40, y + h / 2 + 4, label, size=12, weight="600", fill=colour,
                 anchor="start")
        s += mono(px(start_v) + 12, y + h / 2 + 4, note, size=10, fill=colour,
                  anchor="start", weight="500")
        s += mono(px(end_v) - 12, y + h / 2 + 4, cap, size=9, fill=SOFT, anchor="end")
        y += h + 14

    axis_y = 288
    s += f'<line x1="{x0}" y1="{axis_y}" x2="{x1}" y2="{axis_y}" stroke="{MUTED}" stroke-width="1"/>'
    for v in (450, 470, 490, 510, 525, 545, 565, 580, 600, 615, 635):
        floor = v in (450, 525, 580)
        major = floor or v == 615
        s += (f'<line x1="{px(v)}" y1="{axis_y}" x2="{px(v)}" '
              f'y2="{axis_y + (8 if major else 4)}" '
              f'stroke="{ACCENT if floor else MUTED}" '
              f'stroke-width="{1 if major else 0.6}"/>')
        if major:
            s += mono(px(v), axis_y + 22, str(v), size=9,
                      fill=ACCENT if floor else SOFT, weight="500")
    s += mono(x0, axis_y + 48, "NVIDIA driver branch", size=9, fill=SOFT,
              anchor="start", track="0.10em")

    # The worked example's driver, marked above the axis where nothing else sits.
    s += (f'<circle cx="{px(580)}" cy="{axis_y}" r="4.5" fill="{PAPER}" '
          f'stroke="{ACCENT}" stroke-width="1.4"/>')
    s += mono(px(580) + 14, axis_y + 46, "580.65.06 \u2014 the worked example",
              size=9, fill=ACCENT, anchor="start")

    s += txt(W / 2, 380, "Three floors to remember, not a release-by-release matrix.",
             size=10, fill=MUTED)
    s += txt(W / 2, 398, "The upper bounds limit minor version compatibility only; a "
             "newer driver keeps working through backward compatibility.",
             size=10, fill=SOFT)
    return emit("04", "driver-floors", "Three floors, not a matrix",
                "One minimum driver branch per CUDA major family. Bands are drawn "
                "to scale on the driver-branch axis.",
                "part 2 \u00b7 figure 4", W, vh, s)


def fig05():
    """The three caveats, each with the error it produces."""
    vh = 400
    s = eyebrow(40, 44, "what minor version compatibility does not cover", fill=SOFT)

    items = [
        ("Features spanning\ntoolkit and driver",
         "Some capabilities need code on both sides.",
         "cudaErrorCallRequiresNewerDriver", "= 36", True),
        ("Device code compiled\nto PTX",
         "The driver compiles PTX, so it joins your toolchain.",
         "no error code — it simply will not run", "", False),
        ("The target architecture\nargument to nvcc",
         "A build-time flag. Part 6 of this series owns it.",
         "caught at build time, or not at all", "", False),
    ]
    x = 40
    w = (W - 80 - 2 * 24) / 3
    for title, note, err, val, named in items:
        s += box(x, 76, w, 196, fill="#ffffff",
                 stroke=ACCENT if named else INK, rx=6)
        lines = title.split("\n")
        for i, line in enumerate(lines):
            s += txt(x + w / 2, 116 + i * 20, line, size=13, weight="600",
                     fill=ACCENT if named else INK)
        s += (f'<line x1="{x + 24}" y1="170" x2="{x + w - 24}" y2="170" '
              f'stroke="{RULE}" stroke-width="0.8"/>')
        # wrap the note to two lines by words
        words, line, out = note.split(), "", []
        for word in words:
            if len(line) + len(word) + 1 > 34:
                out.append(line); line = word
            else:
                line = (line + " " + word).strip()
        out.append(line)
        for i, line in enumerate(out[:3]):
            s += txt(x + w / 2, 194 + i * 15, line, size=9.5, fill=SOFT)
        chip_svg, _ = chip(x + w / 2 - (0.62 * 7.5 * len(err) + 16) / 2, 240, err,
                           colour=ACCENT if named else MUTED, size=7.5)
        s += chip_svg
        if val:
            s += mono(x + w / 2, 268, f"value {val[2:]} in driver_types.h", size=8,
                      fill=SOFT)
        x += w + 24

    s += txt(W / 2, 320, "If any one of these bites, the repair is the pre-CUDA-11 one: "
             "install a driver from the same minor version as the toolkit you built "
             "with, or newer.", size=11, fill=MUTED, family=SERIF, style="italic")
    s += legend(vh - 26, W, [
        ("announces itself with a named error", ACCENT, "hollow"),
        ("silent — found at build time or at first launch", INK, "hollow"),
    ])
    return emit("05", "three-caveats", "The three caveats, and what each costs",
                "NVIDIA documents exactly three limits on the minor-version "
                "promise. Only the first reports itself at run time.",
                "part 2 · figure 5", W, vh, s)


def fig06():
    """The two mechanisms span two different gaps in the same stack."""
    vh = 560
    s = eyebrow(40, 44, "two mechanisms, two boundaries", fill=SOFT)

    layers = [
        ("your application", "compiled against a Toolkit", "external"),
        ("libcudart.so.13", "CUDA runtime \u00b7 in the wheel", "focal"),
        ("libcuda.so.1", "CUDA user-mode driver \u00b7 host", "focal"),
        ("nvidia.ko", "kernel-mode driver \u00b7 host", "backend"),
        ("the GPU", "hardware", "external"),
    ]
    x, w = 286, 300
    y = 80
    ys = []
    for name, sub, kind in layers:
        h = 58
        s += node(x, y, w, h, name, sub=sub, kind=kind)
        ys.append((y, y + h))
        y += h + 14

    # minor version compatibility: runtime <-> UMD  (rows 1 and 2), bracket right
    s += vbracket(x + w + 24, ys[1][0] + 8, ys[2][1] - 8,
                  "minor version compatibility", colour=ACCENT, side="right")
    s += mono(x + w + 40, ys[2][1] + 14,
              "the runtime may be NEWER than the driver,",
              size=9, fill=ACCENT, anchor="start")
    s += mono(x + w + 40, ys[2][1] + 28,
              "within one major family",
              size=9, fill=ACCENT, anchor="start")

    # forward compatibility: UMD <-> KMD (rows 2 and 3), bracket left
    s += vbracket(x - 24, ys[2][0] + 8, ys[3][1] - 8,
                  "forward compatibility", colour=LINK, side="left")
    s += mono(x - 40, ys[3][1] + 14, "cuda-compat-13-4 replaces",
              size=9, fill=LINK, anchor="end")
    s += mono(x - 40, ys[3][1] + 28, "this library only",
              size=9, fill=LINK, anchor="end")

    s += txt(W / 2, 492, "The package swaps the user-mode driver and leaves the "
             "kernel module alone. That is exactly why a platform team under "
             "change control can accept it.",
             size=11, fill=MUTED, family=SERIF, style="italic")
    s += legend(vh - 24, W, [
        ("minor version compatibility \u00b7 runtime to user-mode driver", ACCENT, "line"),
        ("forward compatibility \u00b7 user-mode driver to kernel module", LINK, "line"),
    ])
    return emit("06", "two-boundaries", "Two mechanisms, two boundaries",
                "Minor version compatibility spans the runtime and the user-mode "
                "driver. Forward compatibility spans the user-mode driver and the "
                "kernel module. They are not alternatives.",
                "part 2 \u00b7 figure 6", W, vh, s)


def fig08():
    """Six version strings from one install, each with the namespace behind it."""
    vh = 520
    s = eyebrow(40, 44, "one `pip install torch`, six version strings", fill=SOFT)

    rows = [
        ("2.14.0", "PyPI distribution version", "what the resolver matched", False),
        ("2.14.0+cu130", "torch.__version__", "a PEP 440 local label — no semantics", True),
        ("13.0", "torch.version.cuda", "the build-time CUDA, recorded at build", False),
        ("13.0.3", "cuda-toolkit pin", "a meta-package release, not a CUDA release", False),
        ("13.0.96", "nvidia-cuda-runtime pin", "the component wheel's own version", False),
        ("13000", "CUDART_VERSION", "the constant the runtime actually reports", True),
    ]
    y = 74
    for value, namespace, note, focal in rows:
        h = 48
        stroke = ACCENT if focal else INK
        s += box(40, y, W - 80, h, fill=ACCENT_TINT if focal else "#ffffff",
                 stroke=stroke, rx=5)
        s += mono(60, y + h / 2 + 5, value, size=13, fill=stroke, anchor="start",
                  weight="600")
        s += vline(230, y + 10, y + h - 10, stroke=RULE_SOLID, sw=0.8, marker=None)
        s += mono(250, y + h / 2 + 4, namespace, size=10, fill=INK, anchor="start")
        s += vline(510, y + 10, y + h - 10, stroke=RULE_SOLID, sw=0.8, marker=None)
        s += txt(530, y + h / 2 + 4, note, size=10, fill=SOFT, anchor="start")
        y += h + 8

    s += txt(W / 2, y + 32, "Six namespaces. No two of these strings are "
             "interchangeable, and only the last one is compared against anything.",
             size=11, fill=MUTED, family=SERIF, style="italic")
    s += legend(vh - 24, W, [
        ("read as a requirement, but is not one", ACCENT, "box"),
        ("a name in some other namespace", INK, "hollow"),
    ])
    return emit("08", "six-strings", "Six version strings, one install",
                "Each string is correct in its own namespace. Only CUDART_VERSION "
                "takes part in the run-time check.",
                "part 2 · figure 8", W, vh, s)


FIGURES = {1: fig01, 2: fig02, 3: fig03, 4: fig04, 5: fig05, 6: fig06, 8: fig08}

if __name__ == "__main__":
    wanted = [int(a) for a in sys.argv[1:]] or sorted(FIGURES)
    for n in wanted:
        if n == 7:
            print("  fig-07 is routed `mermaid`; see manifest.md for the render command")
            continue
        FIGURES[n]()
