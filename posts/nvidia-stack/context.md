# Series context — The NVIDIA Stack

> Private build memory. Read before starting a member post; update only after a member passes its gate. Keep under 2,000 words.

## Series invariants

- **Audience:** capable software and ML engineers who already use Python, a shell, Docker and a
  framework, and now have to own the NVIDIA layer underneath instead of treating it as weather.
- **Shape:** hybrid — a three-rung ladder (1 → 2 → 3) fanning into thirteen spokes (4–16).
- **Shared promise:** locate any failure to one artifact, size memory before it crashes, choose
  engines and precisions on evidence, and read a profile instead of guessing.
- **The angle every part must obey:** not a CUDA tutorial. Introductory CUDA, reference material
  and spec tables are out of scope by decision — see *What this series will not cover* in
  `plan.md`. Every part is built on a failure with several causes, a decision that must be
  defended, or a mechanism whose canonical explanation is out of date.
- **Terminology:** *compute capability* is a hardware fact written `sm_NN`; Toolkit and driver
  versions are separate artifacts, never "the CUDA version" unqualified. Architectures are named,
  not numbered by marketing tier. Say *fatbinary*, not "the binary". Say *weight-only
  quantization* versus *executed low-precision math* — the series exists to keep those apart.
- **Labs** are shared per thread (compatibility: 2, 6, 16 · kernels: 7, 8, 9 · serving: 11, 12,
  13). Every lab states its tier — A (no GPU), B (one GPU), C (multi-GPU) — because the authoring
  machine has **no NVIDIA GPU**. No number is invented; unmeasured values ship as empty schemas.
- **Visual convention:** caption style `*Figure N. <sentence>.*`, figure numbers from the same
  constants the prose uses, and **every rendered PNG opened and read before the gate** — part 2
  caught a figure that had silently rendered as a browser error page this way.

## Part status

`plan.md` holds what each part owns and hands off; this table holds only what has moved.

| # | Slug | Status | # | Slug | Status |
|---|---|---|---|---|---|
| 1 | what-the-nvidia-stack-actually-is | **ready** | 9 | one-kernel-four-ways | planned |
| 2 | four-cuda-version-numbers | **ready** | 10 | what-tensor-cores-actually-execute | planned |
| 3 | gpu-idle-at-100-percent-utilization | **ready** | 11 | sizing-vram-for-llm-serving | planned |
| 4 | five-causes-of-cuda-out-of-memory | planned | 12 | choosing-an-inference-engine | planned |
| 5 | reading-a-gpu-profile | planned | 13 | nvidia-serving-stack-disambiguated | planned |
| 6 | architecture-aware-tensorrt-llm-cuda-onnx | **ready** | 14 | why-your-multi-gpu-job-hangs | planned |
| 7 | what-changes-between-gpu-generations | planned | 15 | the-parallelism-decision | planned |
| 8 | gpu-memory-hierarchy-after-tma | planned | 16 | jetson-version-lattice | planned (optional) |

Status is `planned`, `researching`, `drafting`, `ready`, or `published`. Nothing is uploaded yet;
parts 1, 2, 3 and 6 are all waiting on Checkpoint C.

## Knowledge established

### Part 1 — What the NVIDIA Stack Actually Is (gate PASS, 4,997 words, 7 figures)

- The layer map is **seven** layers: kernel modules, `libcuda.so.1`, `libcudart.so.13`, compiler
  toolchain, accelerated libraries, framework, serving products. Reuse these names and ordering.
- **Only the driver layer must come from the host.** `libcuda.so.1` is named by PyTorch's binaries
  and shipped by no wheel — the series' load-bearing boundary.
- Nothing installs the stack: via `DT_RPATH`, the **dynamic loader assembles it at import time**.
- `cuda-toolkit` is a real PyPI meta-package and **cuBLAS is declared** through it as an extra.
  Component versions disagree inside one release.
- The traced call at tag `v2.14.0`: `mm_out_cuda` → `at::cuda::blas::gemm<float>` → `cublasSgemm`
  **or** `cublasLtMatmul`, chosen at run time.
- Two claims failed re-verification and were repaired: PyPI's JSON does *not* omit torch's
  `cuda-toolkit` line, and NVIDIA no longer ships only three CUDA image variants.

### Part 2 — The Four CUDA Version Numbers (gate PASS, 4,594 words, 8 figures)

- The four numbers, in order: **KMD** (`nvidia.ko`), **UMD** (`libcuda.so.1`), **the runtime**
  (`libcudart.so.13`, in the wheel), **the Toolkit** (`nvcc`). They replace the word "CUDA".
- `nvidia-smi`'s `Driver Version` and `CUDA Version` are **deprecated** for `KMD Version` and
  `CUDA UMD Version`; the latter is a **ceiling**, "usually, but not always" the Toolkit installed.
- `cudaRuntimeGetVersion` returns a **compile-time constant** since CUDA 12.0 — verified on a
  driverless machine (13000). Both queries encode 1000×major + 10×minor.
- **Minor version compatibility is three numbers**: driver ≥ 450 / 525 / 580 for CUDA 11 / 12 /
  13, per major family, with three caveats (error 36, PTX, `-arch` — part 6's seam).
- **Forward compatibility spans kernel driver to CUDA driver**; minor-version compatibility spans
  runtime to CUDA driver. Reuse it; do not re-derive it.
- `cuda-compat-<major>-<minor>` works only on data center GPUs, select NGC Server Ready RTX SKUs
  and Jetson; `LD_LIBRARY_PATH` is on you; no CUDA–OpenGL/Vulkan interop.
- Pin chain at `torch` 2.14.0: `cuda-toolkit==13.0.3` → `nvidia-cuda-runtime==13.0.96` →
  `CUDART_VERSION` 13000; `+cu130` is a PEP 440 local label with no semantics.

### Part 3 — Why Your GPU Is Idle at 100% Utilization (gate PASS, 6,743 words, 10 figures)

- `nvidia-smi`/NVML utilization is the **share of a 1/6–1 s window with at least one kernel
  executing** — no spatial term. DCGM **SM Activity** (field 1002, renamed
  `DCGM_FI_PROF_SM_UTIL_RATIO` in DCGM 4.6.0) is the spatial counterpart; DCGM's own N/5-blocks
  example reads 100% vs 0.20.
- **Contested, and the post says so:** RL-Scope (MLSys '21) saw 100% at a few percent kernel time;
  the Philly study (ATC '19) calls the counter an upper bound. NVIDIA does not document the
  sampling. `lab/util_probe.py` settles it on hardware; it has not been run.
- The worked example is a **labelled model** (`lab/queue_model.py`; figures 2, 3, 4, 9, 10 import
  it): a 32.0 ms step where the host timer bills 9.6 ms to `loss.item()` and events read 0.0; 53%
  GPU idle; fixes give 22.4 then 15.0 ms (47 → 67 → 100% by definition).
- The rule the later parts reuse: **a sync point costs the overlap it destroys** — a sum of
  per-segment maxes is never below the max of the sums (equation 3).
- Heading `## Host-side sync points` exists for part 5's `#host-side-sync-points` link. CUDA
  Graphs shorten the host lane, never the GPU lane, and forbid sync points.
- PyTorch's default stream is stream 0; its pool streams are non-blocking. At writing: torch
  2.14.0, CUDA 13.4 Update 1; the old C++ Programming Guide is frozen as "Legacy" since 13.0.

### Part 6 — CUDA Architecture Repairs (gate PASS, 8,024 words, 18 figures)

- Compute capability is a **hardware** property; the Toolkit release a **software** one. Neither
  implies the other.
- A fatbinary is an **executable inventory**: real cubins per compute capability plus optional
  virtual PTX. The driver selects an exact image, a compatible one, or JIT-compiles PTX — and
  fails the launch when it can do none of those.
- Testing for an exact `sm_NN` string in the framework's architecture list is the **wrong test**;
  only a warning plus a synchronized core operation decides.
- Failures sort by **phase to owning artifact**: configure/compile, import and dynamic link (an
  undefined symbol is an ABI problem, not a missing SM image), first launch, model load, request.
- The **repair ladder** is ordered by cost: replace the wheel or container, rebuild one
  extension, rebuild the framework, rebuild the serving runtime, pin a different version. A build
  flag can never manufacture product support, a missing operator, or memory.
- Code generation is necessary, not sufficient: CUDA execution, model adapter, feature and
  precision, and memory shapes are four independent gates.
- TensorRT-LLM and ONNX are **sibling branches**, not a pipeline.

## Decisions to preserve

- **Do not re-teach Part 6's ground.** Compute capability, fatbinaries, gencode, the audit matrix,
  the repair ladder and the KV-cache derivation are finished. Link the anchor, recap in three
  sentences at most.
- **Every part names at most one prior part** as a prerequisite. The dependency graph in
  `plan.md` is single-edged by design; if a draft needs two, the cut was wrong.
- **Version numbers are pinned at research time, never at plan time**, and no scoping note is
  quoted unverified. Any version, release name or "X replaces Y" claim needs a dated primary
  source in that part's own ledger.
- **Renames are load-bearing.** Several products were renamed or folded into others while both
  names stayed live in tags and docs. Never assume a product name from memory.
- **Use KMD / UMD / runtime / Toolkit, not "the CUDA version".** Writing "the CUDA version"
  unqualified re-introduces the ambiguity parts 1 and 2 exist to remove.
- **Re-verify any claim shaped "X omits Y" or "there are exactly N"** against the live source
  before it ships. Two such claims failed in part 1 and were repaired.
- **Triton is two unrelated things** — NVIDIA's inference server and the kernel language. Any
  part mentioning either disambiguates on first use.
- **Compute capability is an identifier, not an ordering.** A numerically higher capability can
  lack a feature a lower one has. Never write "newer GPU, so the target is a superset".
- **Cross-links use the canonical URL plus a heading anchor**, never a local path, written in the
  later post rather than by reopening the earlier one.
- **No invented measurements.** Publish the harness and an empty schema, and state every lab's
  tier. A labelled model may carry a worked example (part 3's precedent) if a shipped Tier A
  script computes it, the figures import it, and each caption says "model inputs".
- **The provenance line is settled** (part 3's lab README): capture time, GPU, `sm_NN`, SM count,
  KMD and CUDA UMD read from NVML, torch and its runtime, CPU, Python, instance.
- **Vendor measurement posts with published code** (NVIDIA Technical Blog, PyTorch Blog) are T3
  `source`, with the setup in the Condition column. Forum and poster numbers are never used alone.

## Open threads

- **Part 1's `assets/_figs.py` is lost**; a correction there is an HTML edit plus a re-export.
  Parts 2 and 3 keep their `_figs.py`, `_cover.py` and `_social.py`; later parts should too.

- **Checkpoint S passed on 2026-09-22.** Do not re-propose a different shape. Category is
  `machine-learning` for every part; `series` + `series_position` are the keys the platform reads.
- **Part 9's fourth implementation** may not be measurable fairly; that post drops to three ways
  rather than waiting.
- **Tier B has a harness but no run.** Part 3 ships `step_timing.py` and `util_probe.py` unrun,
  with an empty `results-schema.json`. The first rented GPU session should run them before any
  part 4 or 5 lab, and `util_probe.py`'s result decides whether the RL-Scope reading holds.
- **Part 3's six-lens review ran inline** after all eight agents died on the session limit.
  Re-run it with bounded agents when budget allows.

## Next part brief

- **Part:** 4 — Five Causes of One "CUDA Out of Memory" (`five-causes-of-cuda-out-of-memory`)
- **Tier:** L3, intermediate, ~5,500 words, 9 figures.
- **Can assume:** part 3's execution model, linked at
  `#intuition-two-clocks-and-a-queue` — the host runs ahead, so memory freed in Python may still
  be in use by queued kernels. Part 3 already said, in one sentence, that `cudaFree` can block and
  is why PyTorch caches.
- **Must teach:** the caching allocator, `reserved` vs `allocated`, fragmentation and
  `expandable_segments`, a retained autograd graph, a second process or zombie holding VRAM, and
  non-PyTorch allocations (NCCL, cuBLAS workspaces, the context). One decision tree from evidence
  to exactly one cause.
- **Must not touch:** serving-time capacity planning (part 11) or the profiler workflow (part 5).
- **Worked example:** the same 20 GiB model failing five times for five reasons, with the
  allocator summary after each and the one number that discriminates it.
- **Evidence still needed:** PyTorch's memory docs and snapshot tooling,
  `PYTORCH_CUDA_ALLOC_CONF`, and the allocator source at the release tag.
- **Lab:** the OOM reproductions are Tier B. Look for a Tier A core — allocator arithmetic that
  can run without a GPU — the way part 3 used a queue model, and label it as a model.
- **Handoff:** the memory vocabulary part 11 sizes deployments with.
