# Outline — what-the-nvidia-stack-actually-is

**Series:** The NVIDIA Stack, part 1 of 16 · **Tier:** L2 · **Difficulty:** beginner
**Actual:** 4,934 words · 7 figures · L2 allows 3,000–5,000 words and 5–8 figures.

> Reconstructed on 2026-09-23 from the finished `blog.md`, after the original outline was
> overwritten. Section titles and word counts below are measured from the article as it stands,
> not planned targets.

## The one question this part answers

*What are all these products, and which of them do I actually need?*

## The three reader objectives the series plan assigns to this part

1. Name every layer between a Python tensor call and the GPU, and say which vendor artifact owns each.
2. Say what CUDA-X is, and which of its libraries you are already using without having installed one.
3. Decide whether a given task needs the Toolkit, a framework wheel, a container, or nothing.

## The thesis

**Your CUDA installation is not installed. It is assembled, by the dynamic loader, every time you
`import torch`.** The evidence is the `$ORIGIN`-relative `RPATH` baked into PyTorch's own binaries,
and the one library at the bottom of every chain that no wheel ships.

## What this part must NOT do

- **No version arithmetic.** Part 2 owns why `nvidia-smi` and `nvcc --version` disagree, minor-version
  compatibility and the forward-compatibility package. This part names the artifacts and hands off
  the question.
- **No compute capability, no fatbinaries, no repair advice.** Part 6 owns all three and is drafted.
- **No asynchronous execution model.** Part 3 owns streams, sync points and utilization.
- **No serving product map.** Part 13 owns it.
- **No installation instructions.** The series plan lists installation guides under "will not cover".

## Section structure, as built

| Section | Words | Figure | What the reader can do after it |
|---|---|---|---|
| Insights + level line + lab note | 138 | COVER | state that no single artifact is called CUDA |
| `## Why this matters` | 174 | — | recognise the moment the missing map costs them |
| `## The problem: five different things are called "CUDA"` | 369 | FIG_01 | name the five artifacts the one word conflates |
| `## Worked example: one line of PyTorch, all the way down` | 437 | FIG_02 | name the artifact at each of nine steps of one real call |
| `## Intuition: nothing installs this stack` | 274 | FIG_03 | explain assembly-at-import, and where the analogy to a package manager breaks |
| `## What does the driver actually give you?` | 398 | FIG_04 | separate kernel modules from the user-space libraries the same installer drops |
| `## What is in the CUDA Toolkit, and do you need it?` | 547 | FIG_05 | decide whether they need the Toolkit at all, and read a component version correctly |
| `## What is CUDA-X, and which of it are you already using?` | 483 | FIG_06 | say what CUDA-X is and name the members already on their disk |
| `## Installer, wheel, or container: which do you need?` | 427 | FIG_07 | pick a channel from a task they have not seen before |
| `## Implementation: read the stack before you install it` | 358 | — | inspect a wheel, its metadata and its ELF dynamic section without installing |
| `## Limitations and common mistakes` | 269 | — | avoid the four mistakes this stack actually produces |
| `## Key takeaways` | 141 | — | — |
| `## Try it yourself` | 209 | — | check three predictions on a machine with no GPU |
| `## References` | 710 | — | — |

Seven body sections sits above L2's nominal two-to-four, but each answers a different one of the
three reader objectives or supplies the evidence for one, and the padding test below finds no
overlap. The word total stays inside the tier.

## Figure plan — the route gate, as recorded in `manifest.md`

All seven figures and the cover are routed `placed`. The gate's Q1 (measured data from the ledger)
and Q2 (a captured artefact) do not fire: the numbers shown are inventory, not a measured
comparison, and nothing is a terminal capture. Q3 does not fire either — none of these is
graph-shaped with more than nine nodes or crossing edges. Q4 carries every one of them: proportional
or tabular layouts whose value is a grid of real values that Mermaid cannot place to scale.

| # | Section | The one thing it must communicate | Route | Why |
|---|---|---|---|---|
| FIG_01 | The problem | seven stacked layers, each with its file on disk and the product that ships it | `placed` | seven ruled rows with three columns; a table-shaped layout, not a graph |
| FIG_02 | Worked example | the nine-step descent, each step labelled with the artifact that owns it | `placed` | a linear nine-step trace; ordering is the content, so hand placement is exact |
| FIG_03 | Intuition | which of three supply channels can deliver which layer | `placed` | a six-by-three coverage matrix of ticks and crosses |
| FIG_04 | Driver | kernel modules on one side, driver-installed user-space libraries on the other | `placed` | two parallel columns of five and four boxes, under the nine-node ceiling |
| FIG_05 | Toolkit | nine component wheels of one release, each beside its own version | `placed` | a ruled two-column table; the point is the spread down one column |
| FIG_06 | CUDA-X | that the label spans both Toolkit-bundled and separately-shipped libraries | `placed` | containment: a dashed label drawn over two groups of boxes |
| FIG_07 | Channels | the resolved dependency graph, with two nodes outside `site-packages` | `placed` | nine nodes in two containers with no crossing edges |
| COVER | — | the post's subject at a glance | `placed` | template cover, hand-placed from the post's own layer motif |

No figure takes the `source` route: no cited paper contains a figure that teaches any of this
post's points, so the relevance gate in `paper-figures.md` fails for all of them.

## Lab — hardware tier A

Five files under `lab/`, all uploaded individually and linked from `### Lab downloads`. The tier is
stated in the lab README: **A, no GPU required**. Every number printed in the article was produced
on a machine with no NVIDIA GPU, no driver and no CUDA Toolkit, by reading published archives over
HTTP. `wheelio.py` is shared helpers, `inspect_wheel.py` reads one wheel, `resolve_stack.py` walks
the dependency graph, and `expected-output.txt` is both runs captured on 2026-09-23 for diffing.

## Term map

| Term | First section | What it is | Why it is used here | When it matters |
|---|---|---|---|---|
| kernel module | The problem | a driver component loaded into the Linux kernel | the only part of the stack in kernel space | when the GPU is invisible to every user-space tool at once |
| user-mode driver | The problem | `libcuda.so`, a shared library shipped by the driver package | it is the one layer no wheel can deliver | when a container works and a bare host does not |
| CUDA driver API | Worked example | the C API the driver exposes | everything above it is built on it | when a failure happens before any of your code runs |
| CUDA runtime | The problem | `libcudart.so.13`, the API compiled framework code calls | it belongs to the Toolkit, and travels in wheels | when two copies land in one process |
| CUDA Toolkit | The problem | NVIDIA's development environment | it is what people mean by "installing CUDA", and most readers do not need it | when you compile device code yourself |
| `nvcc` | Toolkit | the CUDA compiler driver, itself a toolchain | its absence is what makes a pip install not a Toolkit install | when a package builds a CUDA extension |
| ATen and the dispatcher | Worked example | PyTorch's C++ tensor library, and the mechanism that picks a backend kernel | it is where "on the GPU" becomes a specific compiled function | when an operation silently runs on the CPU |
| GEMM | Worked example | general matrix multiply, the BLAS name for the operation | it is the routine the trace lands on | when reading any BLAS or profiler documentation |
| cuBLAS / cuBLASLt | Worked example | NVIDIA's dense linear-algebra library, and its newer API surface | the matmul ends there, and PyTorch picks between them at run time | whenever a linear layer is the hot path |
| cuDNN | CUDA-X | NVIDIA's deep-learning primitive library | the largest CUDA-X download in the install, never in the Toolkit | when convolution or attention performance is the question |
| NCCL | CUDA-X | NVIDIA's collective-communication library | it arrives even on a single-GPU machine | when a second GPU appears |
| CUDA-X | CUDA-X | a portfolio label over NVIDIA's GPU-accelerated libraries | it names the layer the reader already uses without installing it | when deciding which library a task needs |
| SONAME / `DT_NEEDED` / `RPATH` | Intuition | the versioned name a library loads under, the entry requesting one, and the search list | they are how the post proves the map instead of asserting it | when the loader cannot find a library |
| ELF | Implementation | the Executable and Linkable Format Linux binaries use | its dynamic section is what the lab reads | when you need to know what a binary will ask for |
| NVML | Driver | the driver's library for reading device state | `nvidia-smi` is built on it, and only NVML has a stable contract | when writing tooling rather than reading a terminal |
| NVIDIA Container Toolkit | Channels | tooling that makes a host GPU usable from a container | it is the cleanest demonstration of the host/image boundary | when a container sees no GPU |

## Cross-links

Part 2 (`four-cuda-version-numbers`) is named three times as the part that owns version arithmetic —
in *Why this matters*, in the Toolkit section and in *Limitations*. It is not yet published, so per
the series plan those are written as the question this part hands off, not as live links.
No backward links: this is part 1.

## Padding test

Each section's "what can the reader do now" answer in the table above is distinct. The two that come
closest are *The problem* (name the artifacts) and *Intuition* (explain how they are assembled) —
they are kept apart by the worked example between them, which is what turns the first into the
second. No section restates another.

## Known defects repaired on 2026-09-23

Two claims did not survive re-verification and were corrected in place; the reasoning is recorded
under *Corrections applied* in `research/ledger.md`.

1. The `WARNING` callout asserted that PyPI's JSON endpoint omits `torch`'s `cuda-toolkit`
   dependency. It does not. The callout now names the mistake that is real and reproducible —
   filtering a dependency list on the prefix `nvidia-`, which misses cuBLAS because it hides inside
   a bracket on a package called `cuda-toolkit`.
2. "NVIDIA publishes exactly three CUDA image variants" is no longer true; the current `nvidia/cuda`
   13.x tag set also carries `cudnn-` and `tensorrt-` flavours. The claim is now about the
   `base` → `runtime` → `devel` chain and the absent driver, both verified in the Dockerfiles.
