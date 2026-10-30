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
  constants the prose uses, and **every rendered PNG opened and read before the gate**.

## Part status

`plan.md` holds what each part owns and hands off; this table holds only what has moved.

| # | Slug | Status | # | Slug | Status |
|---|---|---|---|---|---|
| 1 | what-the-nvidia-stack-actually-is | **ready** | 9 | one-kernel-four-ways | planned |
| 2 | four-cuda-version-numbers | **ready** | 10 | what-tensor-cores-actually-execute | planned |
| 3 | gpu-idle-at-100-percent-utilization | **ready** | 11 | sizing-vram-for-llm-serving | planned |
| 4 | five-causes-of-cuda-out-of-memory | **ready** | 12 | choosing-an-inference-engine | planned |
| 5 | reading-a-gpu-profile | planned | 13 | nvidia-serving-stack-disambiguated | planned |
| 6 | architecture-aware-tensorrt-llm-cuda-onnx | **ready** | 14 | why-your-multi-gpu-job-hangs | planned |
| 7 | what-changes-between-gpu-generations | planned | 15 | the-parallelism-decision | planned |
| 8 | gpu-memory-hierarchy-after-tma | planned | 16 | jetson-version-lattice | planned (optional) |

Status is `planned`, `researching`, `drafting`, `ready`, or `published`. Nothing is uploaded yet;
parts 1, 2, 3, 4 and 6 are all waiting on Checkpoint C.

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
  sampling.
- The worked example is a **labelled model** (`lab/queue_model.py`; figures 2, 3, 4, 9, 10 import
  it): a 32.0 ms step where the host timer bills 9.6 ms to `loss.item()` and events read 0.0; 53%
  GPU idle; fixes give 22.4 then 15.0 ms.
- The rule the later parts reuse: **a sync point costs the overlap it destroys** — a sum of
  per-segment maxes is never below the max of the sums (equation 3).
- CUDA Graphs shorten the host lane, never the GPU lane, and forbid sync points.
- PyTorch's default stream is stream 0; its pool streams are non-blocking. The old C++ Programming Guide is frozen as "Legacy" since 13.0.

### Part 4 — Five Causes of One “CUDA Out of Memory” (gate PASS but the feed-only Story checks, 6,480 words, 9 figures)

- The message is **six numbers from three instruments**: `cudaMemGetInfo` (total, free), NVML's
  compute-process list (other processes, *this process*), the allocator (allocated, reserved but
  unallocated). Graphics processes never appear.
- **Decision order:** growth between iterations first (a leak dies among slivers and reads as
  fragmentation), then unallocated ≥ request, then other holders beyond a ~512 MiB context floor,
  else capacity. `lab/diagnose.py` implements it.
- Before raising, the allocator frees every releasable cached block (not during graph capture), so
  `empty_cache()` never rescues the crashed process. Measured at torch 2.15.0:
  `PYTORCH_CUDA_ALLOC_CONF` beats `PYTORCH_ALLOC_CONF`; a zombie's memory returns before reaping (the
  holder is a live orphan); context 173 MiB lazy, 943 eager; NCCL +548 MiB.
- **Plan correction:** cuBLAS workspaces come from PyTorch's allocator at 2.15.0, so they count as
  allocated, not non-PyTorch.
- **Method for a shared GPU:** emulate the card with `set_per_process_memory_fraction`, never fill
  the machine. On the GB10's unified memory, CUDA free is `MemFree`, CPU allocations shrink it, and
  `nvidia-smi` reports no device memory.

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
- **Tier B has a machine:** AR-01 was granted on 2026-10-30 as an NVIDIA GB10 on the owner's
  network (`access.md`); Part 4 ran there. Part 3's `step_timing.py` and `util_probe.py` are still
  unrun: run them before Part 5's lab, since `util_probe.py` decides the RL-Scope reading.
- **Part 3's six-lens review ran inline** after all eight agents died on the session limit.
  Re-run it with bounded agents when budget allows.

## Next part brief

- **Part:** 5 — Reading a GPU Profile (`reading-a-gpu-profile`)
- **Tier:** L3, intermediate, ~6,500 words, 11 figures.
- **Can assume:** part 3's sync-point rule at `#host-side-sync-points`, its only prerequisite.
- **Must teach:** the workflow, not the counter dictionary: Nsight Systems first, to decide whether
  the time is on the GPU at all; then Nsight Compute on the one kernel that matters; roofline
  reading; why low occupancy is often the correct answer.
- **Must not touch:** fixing what the profile reveals (parts 8 and 9), or memory failures (part 4).
- **Worked example:** one slow model whose first profile blames the data loader, not the GPU; after
  that fix, a second pass earns a kernel profile.
- **Evidence still needed:** the Nsight Systems and Nsight Compute user guides and CUPTI docs, and the roofline model's original paper.
- **Lab:** G3 on the GB10 if `nsys` and `ncu` run there without sudo: the driver can restrict GPU
  counters to administrators (`NVreg_RestrictProfilingToAdminUsers`); if so, raise an access
  request. The GB10 is aarch64 with unified memory and a live desktop.
- **Handoff:** named bottlenecks, which parts 8 and 9 fix.
