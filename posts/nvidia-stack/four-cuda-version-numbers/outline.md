# Outline — The Four CUDA Version Numbers

**Series:** nvidia-stack, part 2 · **Tier:** L2 · **Difficulty:** intermediate
**Budget:** ~4,500 words · **Figures:** 8 · **Lab:** Tier A (no GPU)

## The spine

Four numbers, each owned by a different artifact, each promising something different. Naming them
is the whole post; the compatibility rules fall out of the naming.

| # | Number | Lives in | Printed by | Promises |
|---|---|---|---|---|
| 1 | KMD version (`580.65.06`) | `nvidia.ko` | `nvidia-smi` KMD Version, `/proc/driver/nvidia/version` | which driver branch is loaded — it is not a CUDA number at all |
| 2 | CUDA UMD version (`13.0`) | `libcuda.so.1` | `nvidia-smi` CUDA UMD Version, `cudaDriverGetVersion` | a **ceiling**: the newest CUDA this driver will serve |
| 3 | CUDA runtime version (`13.0`) | `libcudart.so.13` in the wheel | `cudaRuntimeGetVersion`, `torch.version.cuda` | a **compile-time constant**: what the binary was built against |
| 4 | Toolkit version | `nvcc` on `$PATH` | `nvcc --version` | which compiler is installed — says nothing about what runs |

**The rule the post exists to deliver:** number 3 must not exceed number 2, and number 1 must meet
the minimum for number 3's major family. Number 4 is irrelevant at run time.

Five commands print these four numbers, because two of them read the same artifact. That is the
worked example's reveal and it is what makes the title's *four* honest.

## Sections and budget

| Section | Words | Figure | The one thing |
|---|---|---|---|
| Insights + who this is for | 130 | COVER | `nvidia-smi`'s CUDA number is a ceiling, not an inventory |
| Why this matters | 180 | — | the two commands disagree and both are right |
| The problem: four numbers, one word | 360 | FIG_01 | each number is owned by a different artifact |
| Worked example: five commands, four numbers | 660 | FIG_02 | trace every readout to the file that produced it |
| Intuition: a ceiling, a constant, and a compiler | 440 | FIG_03 | a ceiling is compared against a constant; nothing negotiates |
| What does minor version compatibility promise? | 560 | FIG_04, FIG_05 | one driver floor per major family, and three caveats |
| What does forward compatibility actually require? | 560 | FIG_06 | it operates at a different boundary, on a short hardware list |
| Which number do you change? | 520 | FIG_07 | symptom → the one artifact that is wrong |
| The math: what the encoded number compares | 320 | — | `1000×major + 10×minor`, compared as one integer |
| Implementation: predict the answer before installing | 400 | — | read `CUDART_VERSION` out of the wheel |
| Limitations and common mistakes | 250 | FIG_08 | six version strings for one install, from six namespaces |
| Key takeaways + references | 120 | — | |

No `## The math` skip: the encoding is small but load-bearing, because it is what the runtime's
own check compares.

## Figure plan

Every route settled by the gate in `blog-visuals/references/visual-taxonomy.md`.

| # | Shows | Route | Why |
|---|---|---|---|
| FIG_01 | four numbers × artifact, file, command, promise, non-promise | placed | Q4 — a five-column grid of real strings; the value is the row-by-row contrast |
| FIG_02 | five commands collapsing onto four artifacts | placed | Q4 — two commands must visibly land on one artifact; that convergence is the figure |
| FIG_03 | the UMD ceiling as a line, three application runtimes against it | placed | Q4 — positions on a version axis must be to scale |
| FIG_04 | driver-number axis 450→615 with the three major-family bands | placed | Q4 — the bands are drawn to scale on a real number line |
| FIG_05 | the three caveats of minor version compatibility, each with its error code | placed | Q5 — six nodes, no crossings |
| FIG_06 | the two boundaries: minor-version compat between runtime and UMD; forward compat between UMD and KMD | placed | Q4 — the whole point is *which* gap each mechanism spans |
| FIG_07 | symptom → wrong number → smallest repair | mermaid | Q3 — 13 nodes, three parallel paths, and two edges cross |
| FIG_08 | six version strings for one `pip install torch`, each from a different namespace | placed | Q4 — a grid of real strings beside the namespace that produced each |

Budget check: 8 figures at ~4,500 words is one per 560 words, inside the L2 band.

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| kernel-mode driver (KMD) | The problem | the loaded `nvidia.ko` module | it is the only artifact that talks to the hardware | when a version must change on the host |
| user-mode driver (UMD) | The problem | `libcuda.so.1`, the CUDA driver library | it implements the driver API every CUDA program eventually calls | whenever a program reports a CUDA version it did not install |
| CUDA runtime | The problem | `libcudart.so.13`, shipped inside wheels | it is the API frameworks are compiled against | when a wheel runs or refuses to run |
| minor version compatibility | body 1 | a guarantee across one major family | it removes the driver upgrade from a toolkit upgrade | when planning a toolkit bump without a driver bump |
| forward compatibility package | body 2 | `cuda-compat-<major>-<minor>` | it replaces the user-mode driver without touching the kernel module | on datacenter hardware with a frozen driver |
| minimum required driver | body 1 | the floor a toolkit's major family declares | it is what the runtime's own check compares against | before installing any wheel on a fixed host |
| CUDART_VERSION | The math | a compile-time constant in the binary | it is literally the number the runtime reports | when reading a version out of an artifact rather than a command |

## Boundaries

- **Assumes** part 1's layer map, restated in at most three sentences, linked by anchor.
- **Does not touch** compute capability, `sm_NN` or fatbinaries — part 6 owns them. The
  `-arch=sm_xx` caveat is named as a caveat and handed off, never explained.
- **Does not re-derive** that these are separate artifacts, that component versions disagree
  inside one release, or that `nvidia-smi`'s `CUDA Version` field is deprecated. Part 1 paid for
  all three.
- **Hands off** the version model that part 6's audit matrix is written against.
