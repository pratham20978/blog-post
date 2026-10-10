# Source ledger — what-the-nvidia-stack-actually-is

## Brief

- **Series:** The NVIDIA Stack, part 1 of 16 (`nvidia-stack`)
- **Subject:** machine-learning systems and GPU platform architecture
- **Depth:** L2 standard · **Difficulty:** beginner
- **Audience:** engineers who use Python, a shell and a framework, and now have to own the NVIDIA
  layer underneath instead of treating it as weather
- **Reader outcome:** name every layer between a Python tensor call and the GPU and say which
  vendor artifact owns each; say what CUDA-X is and which of its libraries they already have
  without having installed one; decide whether a task needs the Toolkit, a wheel, a container, or
  nothing
- **Deliberately deferred:** version arithmetic and compatibility rules (part 2), the asynchronous
  execution model (part 3), compute capability and fatbinaries (part 6), the serving product map
  (part 13)
- **Hardware tier: A.** Every measurement in this post was produced on a machine with no NVIDIA
  GPU, no driver and no CUDA Toolkit, by reading published archives and metadata over HTTP. No
  command output is presented as a captured run on NVIDIA hardware.
- **Version discipline:** no version, filename or product name is stated from memory. Everything
  was pinned against a primary source fetched on 2026-09-22 or re-verified on 2026-09-23.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S01 | T1 | Owens, Luebke, Govindaraju, Harris, Krüger, Lefohn, Purcell, "A Survey of General-Purpose Computation on Graphics Hardware" | Computer Graphics Forum 26(1):80–113 | 2007 | 10.1111/j.1467-8659.2007.01012.x | peer-reviewed | https://doi.org/10.1111/j.1467-8659.2007.01012.x | 2026-09-22 |
| S02 | T1 | Lindholm, Nickolls, Oberman, Montrym, "NVIDIA Tesla: A Unified Graphics and Computing Architecture" | IEEE Micro 28(2):39–55 | 2008 | 10.1109/MM.2008.31 | peer-reviewed | https://doi.org/10.1109/MM.2008.31 | 2026-09-22 |
| S03 | T4 | Nickolls, Buck, Garland, Skadron, "Scalable Parallel Programming with CUDA" | ACM Queue 6(2):40–53 — ACM's practitioner magazine, not a refereed venue | 2008 | 10.1145/1365490.1365500 | practitioner | https://doi.org/10.1145/1365490.1365500 | 2026-09-22 |
| S04 | T1 | Jia, Maggioni, Staiger, Scarpazza, "Dissecting the NVIDIA Volta GPU Architecture via Microbenchmarking" | — (preprint; no venue established) | 2018 | arXiv:1804.06826 | preprint | https://arxiv.org/abs/1804.06826 | 2026-09-22 |
| S05 | T1 | Python Packaging Authority, "Binary distribution format" — the wheel specification | PyPA packaging specifications | 2026 | PEP 427 | standard | https://packaging.python.org/en/latest/specifications/binary-distribution-format/ | 2026-09-22 |
| S06 | T1 | Python Packaging Authority, "Dependency specifiers" — the extras syntax | PyPA packaging specifications | 2026 | PEP 508 | standard | https://packaging.python.org/en/latest/specifications/dependency-specifiers/ | 2026-09-22 |
| S07 | T2 | `ld.so(8)` manual page — `RPATH`, `RUNPATH` and `$ORIGIN` search order | Linux man-pages | 2026 | Linux man-pages 6.19 | official-docs | https://man7.org/linux/man-pages/man8/ld.so.8.html | 2026-09-22 |
| S08 | T2 | NVIDIA CUDA C++ Programming Guide, "The CUDA platform" | — | 2026 | Programming Guide v13.4.2 | official-docs | https://docs.nvidia.com/cuda/cuda-programming-guide/01-introduction/cuda-platform.html | 2026-09-22 |
| S09 | T2 | NVIDIA CUDA C++ Programming Guide, "NVCC: The NVIDIA CUDA Compiler" | — | 2026 | Programming Guide v13.4.2 | official-docs | https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/nvcc.html | 2026-09-22 |
| S10 | T2 | NVIDIA CUDA Driver API, "Difference between the driver and runtime APIs" | — | 2026 | — | official-docs | https://docs.nvidia.com/cuda/cuda-driver-api/driver-vs-runtime-api.html | 2026-09-22 |
| S11 | T2 | NVIDIA CUDA Toolkit Release Notes — the component table and its per-component versions | — | 2026 | CUDA Toolkit 13.4 Update 1 | official-docs | https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html | 2026-09-22 |
| S12 | T2 | NVIDIA CUDA Installation Guide for Linux — §8 Pip Wheels, package-manager and runfile channels | — | 2026 | Installation Guide v13.4 | official-docs | https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html | 2026-09-23 |
| S13 | T2 | NVIDIA Linux driver README, "Listing of Installed Components" | — | 2026 | driver release 615.71.09 | official-docs | https://us.download.nvidia.com/XFree86/Linux-x86_64/615.71.09/README/installedcomponents.html | 2026-09-22 |
| S14 | T2 | NVIDIA Linux driver README, "Open Linux Kernel Modules" | — | 2026 | driver release 615.71.09 | official-docs | https://us.download.nvidia.com/XFree86/Linux-x86_64/615.71.09/README/kernel_open.html | 2026-09-22 |
| S15 | T2 | NVIDIA Management Library (NVML) API Reference | — | 2026 | — | official-docs | https://docs.nvidia.com/deploy/nvml-api/index.html | 2026-09-22 |
| S16 | T2 | `nvidia-smi` manual — the query-field definitions | — | 2026 | — | official-docs | https://docs.nvidia.com/deploy/nvidia-smi/index.html | 2026-09-23 |
| S17 | T2 | NVIDIA, "NVIDIA CUDA-X" | — | undated page | — | official-docs | https://www.nvidia.com/en-us/technologies/cuda-x/ | 2026-09-22 |
| S18 | T2 | NVIDIA, "CUDA-X GPU-Accelerated Libraries" index | — | undated page | — | official-docs | https://developer.nvidia.com/gpu-accelerated-libraries | 2026-09-23 |
| S19 | T2 | NVIDIA CUDA Libraries documentation hub — where the API manuals for these libraries live | — | 2026 | — | official-docs | https://docs.nvidia.com/cuda-libraries/index.html | 2026-09-22 |
| S20 | T2 | NVIDIA Container Toolkit, Architecture Overview | — | 2026 | — | official-docs | https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/arch-overview.html | 2026-09-22 |
| S21 | T2 | NVIDIA CUDA Binary Utilities — `cuobjdump` and friends | — | 2026 | — | official-docs | https://docs.nvidia.com/cuda/cuda-binary-utilities/index.html | 2026-09-22 |
| S22 | T2 | NVIDIA Compute Sanitizer documentation | — | 2026 | — | official-docs | https://docs.nvidia.com/compute-sanitizer/ComputeSanitizer/index.html | 2026-09-22 |
| S23 | T3 | NVIDIA/open-gpu-kernel-modules — the open kernel modules and their README | — | 2026 | source release 615.71.09 | source | https://github.com/NVIDIA/open-gpu-kernel-modules | 2026-09-22 |
| S24 | T3 | libnvidia-container `src/nvc_info.c` at a pinned commit — the exact host files injected into a container | — | 2026 | commit 24a848d9f0f31a40d047a8178b86eb024548546e | source | https://github.com/NVIDIA/libnvidia-container/blob/24a848d9f0f31a40d047a8178b86eb024548546e/src/nvc_info.c | 2026-09-22 |
| S25 | T3 | PyTorch `aten/src/ATen/native/native_functions.yaml` at tag v2.14.0 | — | 2026 | tag v2.14.0 | source | https://github.com/pytorch/pytorch/blob/v2.14.0/aten/src/ATen/native/native_functions.yaml | 2026-09-22 |
| S26 | T3 | PyTorch `aten/src/ATen/native/cuda/Blas.cpp` at tag v2.14.0 | — | 2026 | tag v2.14.0 | source | https://github.com/pytorch/pytorch/blob/v2.14.0/aten/src/ATen/native/cuda/Blas.cpp | 2026-09-22 |
| S27 | T3 | PyTorch `aten/src/ATen/cuda/CUDABlas.cpp` at tag v2.14.0 | — | 2026 | tag v2.14.0 | source | https://github.com/pytorch/pytorch/blob/v2.14.0/aten/src/ATen/cuda/CUDABlas.cpp | 2026-09-22 |
| S28 | T3 | `torch` 2.14.0 on PyPI — the wheel, its `METADATA`, and the ELF dynamic sections of the libraries inside it | — | 2026 | torch 2.14.0, published 2026-09-02 | source | https://pypi.org/project/torch/2.14.0/ | 2026-09-23 |
| S29 | T3 | `cuda-toolkit` on PyPI — the meta-package and its per-extra requirements | — | 2026 | cuda-toolkit 13.0.3 | source | https://pypi.org/project/cuda-toolkit/ | 2026-09-23 |
| S30 | T3 | `nvidia-cublas` on PyPI, and the `nvidia-cublas-cu13` placeholder beside it | — | 2026 | nvidia-cublas 13.1.1.3; nvidia-cublas-cu13 0.0.1 | source | https://pypi.org/project/nvidia-cublas/ | 2026-09-23 |
| S31 | T3 | `nvidia-cuda-runtime` on PyPI | — | 2026 | nvidia-cuda-runtime 13.0.96 | source | https://pypi.org/project/nvidia-cuda-runtime/ | 2026-09-23 |
| S32 | T3 | NVIDIA CUDA container images — the `base`, `runtime` and `devel` Dockerfiles | — | 2026 | `dist/*/ubuntu2204/{base,runtime,devel}/Dockerfile`, master | source | https://gitlab.com/nvidia/container-images/cuda | 2026-09-23 |
| S33 | T3 | Our own lab run, captured 2026-09-23 on a machine with no NVIDIA GPU, driver or Toolkit — `inspect_wheel.py` and `resolve_stack.py`, output preserved in `lab/expected-output.txt` | — | 2026 | tier A, 2026-09-23 | source | https://pypi.org/project/torch/2.14.0/ | 2026-09-23 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | Google Scholar | `survey GPU computing`, sorted by citations | Owens et al. 2007 (Computer Graphics Forum) as the most-cited GPU-computing survey, and Owens et al. 2008 (Proceedings of the IEEE) behind it; both refereed with DOIs |
| 2 | 1 | Crossref REST API | `query.bibliographic=NVIDIA Tesla A Unified Graphics and Computing Architecture` | 10.1109/MM.2008.31, IEEE Micro 28(2):39–55, 2008-03 — the architects' own account of the unified architecture |
| 3 | 1 | Crossref REST API | `query.bibliographic=Scalable Parallel Programming with CUDA` | Five distinct 2008 records share this title. The four-author Queue article is 10.1145/1365490.1365500; ACM Queue is a practitioner magazine, so it is labelled as such and does not count toward the peer-reviewed floor |
| 4 | 1 | Crossref REST API | `query.bibliographic=A survey of general-purpose computation on graphics hardware` | 10.1111/j.1467-8659.2007.01012.x, Computer Graphics Forum 26(1):80–113, seven authors |
| 5 | 1 | arXiv | `Dissecting the NVIDIA Volta GPU Architecture via Microbenchmarking` | arXiv:1804.06826. No venue established, so it is cited as a preprint and only as evidence that parts of this stack are recovered by measurement rather than documentation |
| 6 | 4 | Google Scholar | forward citations from Lindholm 2008, looking for work that corrects the vendor description | The microbenchmarking line, of which the Volta dissection above is the clearest instance for this post's purpose |
| 7 | 2 | docs.nvidia.com | CUDA C++ Programming Guide, "The CUDA platform" and "NVCC" | The driver/Toolkit boundary; the runtime as one of the Toolkit's libraries; `nvcc` as a toolchain driving `cudafe++`, `ptxas`, `nvlink` and `fatbinary`; `libcudart_static` as the default link |
| 8 | 2 | docs.nvidia.com | CUDA Driver API, driver-vs-runtime page | The runtime API sits on the driver API; the driver API is what `libcuda.so` exposes |
| 9 | 2 | docs.nvidia.com | CUDA Toolkit Release Notes, component table | Each Toolkit component carries its own version, none of which is the release number |
| 10 | 2 | docs.nvidia.com | CUDA Installation Guide for Linux, §8 Pip Wheels and the runfile section | Verbatim: the pip packages "are intended for runtime use and do not currently include developer tools (these can be installed separately)". Also verbatim: "The suffixed `-cu13` package names on PyPI are deprecated placeholders and should not be used", and the default install location `/usr/local/cuda-13.4` with a `/usr/local/cuda` symlink |
| 11 | 2 | docs.nvidia.com | `nvidia-smi` manual, query-field definitions | Verbatim: "CUDA Version — Deprecated; use CUDA UMD Version instead" and "CUDA UMD Version — The CUDA 'User Mode Driver' version. This is the latest CUDA version supported by the driver. This is usually, but not always, the version of the CUDA toolkit installed on the system" |
| 12 | 2 | us.download.nvidia.com | driver 615.71.09 README, installed components and kernel modules | Five kernel modules by filename; `/usr/lib/libcuda.so.<driver version>`; `libnvidia-ml.so.<driver version>`; `libnvidia-ptxjitcompiler.so.<driver version>`; `nvidia-uvm.ko` loaded when a CUDA program starts; open and proprietary flavours with identical user-space components |
| 13 | 2 | docs.nvidia.com | CUDA-X pages and the CUDA Libraries documentation hub | The brand carries no version and no installer; the two CUDA-X pages do not list the same members; the reference hub where these libraries' API manuals live never uses the term |
| 14 | 2 | docs.nvidia.com | Container Toolkit architecture overview | The runtime hook configures the container from the host; the driver is a host prerequisite, not an image component |
| 15 | 5 | GitHub | `libnvidia-container` `src/nvc_info.c` at a pinned commit | The literal list of host files injected into a container — driver-owned libraries and binaries only, and no Toolkit library |
| 16 | 5 | GitHub | PyTorch at tag `v2.14.0`: `native_functions.yaml`, `native/cuda/Blas.cpp`, `cuda/CUDABlas.cpp` | `mm` as a structured delegate to `mm.out`; `TORCH_IMPL_FUNC(mm_out_cuda)`; `at::cuda::blas::gemm<float>`; `gemm_internal` branching on a preferred backend; `cublasSgemm` against `cublasLtMatmulAlgoGetHeuristic` plus `cublasLtMatmul` |
| 17 | 5 | PyPI JSON API | `/pypi/torch/2.14.0/json`, and the same release's wheel `METADATA` | The declared CUDA dependencies: `cuda-toolkit[…eleven extras…]==13.0.3`, `cuda-bindings`, and four suffixed `nvidia-*` packages. **Re-checked 2026-09-23: both the release and project JSON endpoints return the `cuda-toolkit` line** — see the correction note below |
| 18 | 5 | PyPI JSON API | `/pypi/cuda-toolkit/13.0.3/json`, grouped by extra | The eleven extras PyTorch names resolve to eleven distributions. An `nvcc` extra exists and PyTorch does not request it, so `nvidia-cuda-nvcc` never lands |
| 19 | 5 | PyPI JSON API | `nvidia-cublas`, `nvidia-cublas-cu13`, `nvidia-cuda-runtime` | The live unsuffixed distributions, and the `0.0.1` placeholder whose summary reads "DEPRECATED: Use nvidia-cublas instead" |
| 20 | 5 | files.pythonhosted.org (HTTP Range reads) | ZIP central directories and ELF dynamic sections of the torch and NVIDIA wheels | Every size, filename, `SONAME`, `DT_NEEDED` and `DT_RPATH` quoted in the post, read without installing anything. Captured in `lab/expected-output.txt` |
| 21 | 5 | GitLab API | `nvidia/container-images/cuda`, `dist/*/ubuntu2204/{base,runtime,devel}/Dockerfile` | The chain is explicit: `devel` is `FROM …-runtime-…`, `runtime` is `FROM …-base-…`, `base` is `FROM ubuntu:22.04` and installs `cuda-cudart-…` only. `devel` sets `ENV LIBRARY_PATH /usr/local/cuda/lib64/stubs`. No image installs a driver; `base` instead declares `NVIDIA_REQUIRE_CUDA` with a host driver constraint |
| 22 | 5 | Docker Hub API | `nvidia/cuda` tags matching `13.` | **Correction found.** Alongside `base`, `runtime` and `devel`, the 13.x tag set also carries `cudnn-runtime`, `cudnn-devel`, `tensorrt-runtime` and `tensorrt-devel`. "Exactly three variants" is no longer accurate — see the correction note below |
| 23 | 5 | man7.org | `ld.so(8)` | `$ORIGIN` semantics and the `RPATH`/`RUNPATH` search order that makes the site-packages assembly work |
| 24 | 2 | packaging.python.org | wheel binary-distribution format, and dependency specifiers | The archive layout the lab reads, and the `name[extra]` syntax that hides cuBLAS inside a bracket |

## Corrections applied on 2026-09-23

Two claims in an earlier draft of this post did not survive re-verification. Both were repaired in
`blog.md` rather than left standing.

1. **PyPI's JSON endpoint does not omit the `cuda-toolkit` dependency.** The draft asserted that
   the summary endpoint "omits the `cuda-toolkit[...]` line entirely", and built the post's
   `WARNING` callout on it. Re-fetched on 2026-09-23, both `/pypi/torch/json` and
   `/pypi/torch/2.14.0/json` return seventeen `requires_dist` entries *including* the
   `cuda-toolkit[…]==13.0.3` line. The lab's own captured output had always hedged correctly
   ("PyPI's JSON summary can disagree with this"); the article had hardened that hedge into a
   false absolute. The claim is now stated as the habit it justifies — read `Requires-Dist` from
   the wheel, because the archive is what the installer consumes — without asserting a
   discrepancy that is not reproducible.
2. **NVIDIA does not publish "exactly three" CUDA image variants.** The `base` → `runtime` →
   `devel` chain is real and verified in the Dockerfiles, but the current `nvidia/cuda` 13.x tag
   set also carries `cudnn-runtime`, `cudnn-devel`, `tensorrt-runtime` and `tensorrt-devel`. The
   claim is now about the chain and the absent driver, which is what the argument actually needs.

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | `libcuda.so` is the user-mode driver: the shared library that exposes the CUDA driver API, the low-level entry point the CUDA runtime is built on top of | S08, S10 | NVIDIA's docs are not internally consistent about the spelling — the Programming Guide writes `cuda.so`, the Compatibility document `libcuda.so`. The post uses the form matching the installed filename |
| L02 | The CUDA runtime is one of the libraries the CUDA Toolkit provides, and it is the API a program calls to allocate memory and launch work. It belongs to the Toolkit, not to the driver | S08, S11 | — |
| L03 | The NVIDIA driver is required for every use of the GPU, display included, and the rest of the CUDA platform is built on it | S08 | — |
| L04 | The Linux driver contains five kernel modules — `nvidia.ko`, `nvidia-modeset.ko`, `nvidia-uvm.ko`, `nvidia-drm.ko`, `nvidia-peermem.ko`. Two carry the compute path; `nvidia-modeset.ko` programs the display engine and `nvidia-peermem.ko` serves RDMA from a network adapter into GPU memory | S14, S13 | Driver release 615.71.09. NVIDIA spells the filenames with hyphens; `lsmod` shows underscores, a Linux kernel convention rather than an NVIDIA one |
| L05 | `nvidia-uvm.ko` provides the CPU–GPU shared memory CUDA uses, and NVIDIA says it generally loads when a CUDA program starts rather than at boot | S13 | — |
| L06 | The modules ship in two mutually exclusive flavours — open, dual-licensed MIT/GPLv2 and published on GitHub each release, and proprietary — with identical user-space components. The proprietary flavour covers Turing through Hopper; Blackwell and later are open-module-only | S14, S23 | Driver release 615.71.09. So the flavour is a licensing and hardware-support question, not a behavioural one |
| L07 | The driver package installs the user-mode driver at `/usr/lib/libcuda.so.<driver version>`, with an `ldconfig` symlink beside it, and the README lists each installed file with the driver version baked into its name | S13 | Paths vary by distribution. The version suffix tracks the driver, never the Toolkit |
| L08 | The PTX just-in-time compiler is a driver artifact too, installed as `libnvidia-ptxjitcompiler.so.<driver version>` | S13 | — |
| L09 | `libnvidia-ml.so.<driver version>` is the NVIDIA Management Library, the driver's own library for reading device state, and `nvidia-smi` is a program built on it | S13, S15 | — |
| L10 | The `nvidia-smi` manual marks its `CUDA Version` field deprecated in favour of `CUDA UMD Version`, defined as the CUDA user-mode driver version — "the latest CUDA version supported by the driver", and "usually, but not always, the version of the CUDA toolkit installed on the system" | S16 | Verbatim from the query-field definitions, re-read 2026-09-23. The new label names the artifact the number came from |
| L11 | `nvidia-smi`'s output format carries no backward-compatibility guarantee, while NVML's bindings do, so tooling should read NVML rather than parse the command | S16, S15 | — |
| L12 | `nvcc` links the CUDA runtime statically by default — `libcudart_static` unless `--cudart=shared` is passed — so a binary built that way already carries its runtime | S09 | Programming Guide v13.4.2. PyTorch's published binaries link dynamically, which is why a PyTorch user does see a shared `libcudart` |
| L13 | `libcudart.so.13` names no driver library in its dynamic section and imports none of its symbols: the runtime looks the driver up by name once the process is running rather than being bound to it at build time | S33 | Measured from the published wheel's ELF dynamic section on 2026-09-23. This is a fact about linking, not about calling — the runtime still reaches the driver at run time |
| L14 | `nvcc` is a toolchain rather than a single compiler: it splits device code from host code, hands each to its own compiler, and drives `cudafe++`, `ptxas`, `nvlink` and `fatbinary` among others | S09 | — |
| L15 | `nvcc -v` prints every tool invocation in the workflow, and `-keep` leaves the intermediates on disk | S09 | — |
| L16 | The Toolkit's tools include `cuobjdump` for inspecting compiled GPU binaries, Compute Sanitizer for correctness checking, `cuda-gdb`, and the Nsight Systems / Nsight Compute measurement pair. Every component carries its own version number rather than the Toolkit's | S11, S21, S22 | Component membership is per-release and must be pinned to a named Toolkit version |
| L17 | The Toolkit's accelerated libraries are cuBLAS, cuFFT, cuRAND, cuSOLVER and cuSPARSE, and inside `cuda-toolkit==13.0.3` their versions are 13.1.1.3, 12.0.0.61, 10.4.0.35, 12.0.4.66 and 12.6.3.3 — not one of which is the release number | S11, S29 | Exactly as the meta-package's per-extra requirements read on 2026-09-23. A different Toolkit release gives different component versions |
| L18 | On Linux the Toolkit installs to `/usr/local/cuda-<version>` with a `/usr/local/cuda` symlink aimed at it, and since CUDA 13.4 the Linux driver is distributed separately rather than bundled with it | S12 | Installation Guide v13.4. The unbundling is recent and is the kind of sentence that is wrong if written from memory |
| L19 | NVIDIA publishes a meta-package on PyPI literally named `cuda-toolkit` that contains no software. It pulls in component wheels selected by extras — the `name[a,b]` syntax that picks optional dependency groups | S29, S06 | cuda-toolkit 13.0.3 |
| L20 | With CUDA 13 the component wheels dropped the CUDA major-version suffix — `nvidia-cuda-runtime` replaces `nvidia-cuda-runtime-cu12` — and NVIDIA's own installation guide calls the suffixed `-cu13` names "deprecated placeholders" that "should not be used". `nvidia-cublas-cu13` is version 0.0.1 with the summary "DEPRECATED: Use nvidia-cublas instead" | S12, S30 | State as of 2026-09-23. When the transition happened was not established and the post does not date it |
| L21 | The suffix did not disappear everywhere: `nvidia-cudnn-cu13`, `nvidia-nccl-cu13`, `nvidia-cusparselt-cu13` and `nvidia-nvshmem-cu13` remain suffixed, live and maintained, which is why both spellings appear in one dependency list | S28 | torch 2.14.0's declared Linux dependencies. These four are versioned on their own release trains rather than the Toolkit's |
| L22 | NVIDIA documents its CUDA pip wheels as intended for runtime use, stating they "do not currently include developer tools (these can be installed separately)" | S12 | Installation Guide for Linux, §8 Pip Wheels, re-read 2026-09-23 |
| L23 | CUDA-X is a portfolio label, not an artifact: there is no `libcudax.so`, no CUDA-X version and nothing to download called CUDA-X, and NVIDIA's own CUDA Libraries documentation hub — where these libraries' API manuals live — never uses the term | S17, S18, S19 | Pages as they read on 2026-09-22 and 2026-09-23. Both CUDA-X pages are marketing pages carrying no version and no last-updated date |
| L24 | NVIDIA's two CUDA-X pages do not list the same members, so any CUDA-X list is a snapshot rather than a specification an install can be checked against | S17, S18 | As of 2026-09-23 |
| L25 | The `torch` wheel ships thirteen shared libraries and not one of them is cuBLAS, cuDNN, the CUDA runtime, cuFFT, cuSOLVER, cuRAND or cuSPARSE | S33, S28 | torch 2.14.0, CPython 3.12, manylinux_2_28 x86_64, read from the archive on 2026-09-23 |
| L26 | That wheel is 554.6 MB to download, holds 13,043 entries and 1144.2 MB unpacked, and its two largest libraries are `libtorch_cuda.so` at 502.8 MB and `libtorch_cpu.so` at 446.3 MB | S33, S28 | Same wheel and date. Download size is the compressed archive |
| L27 | A zip keeps its central directory at the end of the file, so a client that can issue HTTP Range requests reads the listing and skips the payload — here three requests and 1.2 MB on the wire to list a 554.6 MB archive | S05, S33 | Requires a Range-capable server; `files.pythonhosted.org` is one |
| L28 | `cublasSgemm` lives in `libcublas.so.13`, which is not inside the PyTorch wheel. The wheel's own libraries carry an `RPATH` pointing at `site-packages/nvidia/cu13/lib`, and that is where the loader finds it | S33, S30 | Measured from the wheel's ELF dynamic sections |
| L29 | `libcuda.so.1` is named by PyTorch's binaries — `libcaffe2_nvrtc.so` requests it — and is shipped by no wheel in the dependency graph. It resolves to the host driver, always | S33 | The single unresolved library in the whole resolved graph, which is the post's central argument |
| L30 | The number after `.so` in a request like `libcublas.so.13` is that library's own major version: cuBLAS asks for 13 and cuSOLVER for 12 in the same binary, and neither number is "the CUDA version" | S33 | Read from one library's `DT_NEEDED` entries |
| L31 | PyTorch's compiled libraries carry `$ORIGIN`-relative `RPATH` entries — `$ORIGIN/../../nvidia/cudnn/lib` and five more — which resolve to sibling folders inside `site-packages`, so the loader assembles the stack at import time | S33, S07 | `$ORIGIN` means the directory containing the library being loaded |
| L32 | The `torch` wheel's own `METADATA` declares `cuda-toolkit[cublas,cudart,cufft,cufile,cupti,curand,cusolver,cusparse,nvjitlink,nvrtc,nvtx]==13.0.3` plus four `nvidia-*` packages, and resolving that graph gives 32 packages and 90 shared libraries | S28, S33 | torch 2.14.0 on Linux x86_64. cuBLAS appears only as the word `cublas` inside the bracket, under no package name beginning `nvidia-` |
| L33 | PyPI's JSON metadata and the wheel's own `METADATA` are two different surfaces describing one artifact, and the wheel is the one an installer consumes — so a dependency question is settled by reading `Requires-Dist` out of the archive | S05, S28 | **Corrected 2026-09-23.** An earlier draft claimed the JSON endpoint omits the `cuda-toolkit` line; re-fetched, both PyPI JSON endpoints return it. No discrepancy is asserted — only that the archive is the authoritative surface |
| L34 | cuBLAS is the dense linear-algebra library that runs the traced matrix multiply; cuDNN holds the convolution and attention primitives and its wheel ships ten libraries totalling 887.7 MB; NCCL ships `libnccl.so.2` at 343.9 MB and runs the collectives between GPUs. `nvidia-cudnn-cu13` depends on `nvidia-cublas` directly, so cuBLAS would land even without PyTorch's extra | S33 | Sizes measured on 2026-09-23 from the build of each wheel that was current that day — cuDNN 9.26.0.51, NCCL 2.32.3 — which are **newer than the versions torch 2.14.0 pins** (9.24.0.43 and 2.30.7). The lab's resolver walks names, not `==` pins. The article says "current wheel" for this reason; the teaching point holds under either build |
| L35 | `libcublas.so.13` is 57.6 MB and `libcublasLt.so.13` is 545.5 MB — the second larger than `libtorch_cuda.so`, making NVIDIA's matrix-multiply library the biggest single file in a PyTorch GPU install | S33 | Uncompressed sizes read from the central directory of `nvidia-cublas` **13.8.0.4**, the build current on 2026-09-23 — not the 13.1.1.3 that `cuda-toolkit==13.0.3` pins and that figure 5 lists. The article says "in the build current today" so the two are not conflated |
| L36 | In PyTorch's operator registry `mm` is declared in `native_functions.yaml` as a structured delegate to `mm.out`, and that file is turned by the build into the dispatcher's tables rather than being documentation | S25 | PyTorch at tag v2.14.0 |
| L37 | `TORCH_IMPL_FUNC(mm_out_cuda)` lives in `aten/src/ATen/native/cuda/Blas.cpp` and reaches `at::cuda::blas::gemm<float>` through `addmm_out_cuda_impl` — the boundary where PyTorch stops and NVIDIA's code starts | S26 | Same tag |
| L38 | `gemm_internal<float>` branches on a preferred-backend setting: the classic path calls `cublasSgemm`, and the cuBLASLt path calls `cublasLtMatmulAlgoGetHeuristic` to ask the library which algorithm to use before calling `cublasLtMatmul` | S27 | Same tag. Which branch a given matmul takes depends on dtype, shape and configuration |
| L39 | Which GPU machine code actually runs is decided inside cuBLAS at the moment of the call, by heuristic on the Lt path — so the kernel cannot be named by reading the framework's source | S27 | A property of the stack. Answering it for a specific machine needs cuBLAS's own logging, not source reading |
| L40 | NVIDIA's CUDA images are built as a chain — `devel` is `FROM` the `runtime` image, `runtime` is `FROM` the `base` image, and `base` is `FROM` a plain distribution image — and none of them installs a driver. `base` instead declares a host driver requirement through `NVIDIA_REQUIRE_CUDA` | S32 | **Corrected 2026-09-23.** An earlier draft said NVIDIA publishes "exactly three" variants; the current `nvidia/cuda` 13.x tag set also carries `cudnn-` and `tensorrt-` flavours of runtime and devel. The chain and the absent driver are what the argument needs, and both are verified in the Dockerfiles |
| L41 | The `devel` image sets `LIBRARY_PATH` to `/usr/local/cuda/lib64/stubs`, so code that will run on a GPU can still be linked inside a container with no driver present | S32 | Verbatim `ENV LIBRARY_PATH /usr/local/cuda/lib64/stubs` in the devel Dockerfile |
| L42 | What the container runtime injects from the host is driver-owned only — `nvidia-smi`, the driver libraries and their companions — and no Toolkit library is ever injected | S24, S20 | Read from `libnvidia-container`'s own file list at a pinned commit, which is the authoritative enumeration |
| L43 | GPUs were programmed through graphics APIs until a unified architecture for general-purpose computation arrived, described by NVIDIA's own architects in a refereed venue in 2008 | S02, S01 | The 2007 survey is the record of the era before it |
| L44 | The C-like programming model for that architecture was published alongside it in 2008 by the people who built it | S03 | ACM Queue is ACM's practitioner magazine, not a refereed research venue, and the post labels it that way |
| L45 | Parts of this stack remain undocumented enough that researchers recover their behaviour by microbenchmarking rather than by reading a manual | S04 | A preprint with no established venue, cited only as evidence that the practice exists — not for any specific architectural number |

## Figure candidates

No figure in this post is reproduced from a paper. The cited papers support historical and
bibliographic claims rather than mechanisms the post draws, so the relevance gate in
`blog-visuals/references/paper-figures.md` fails for all of them and the `source` route is not
used. Every figure is our own analysis of artifacts we fetched and measured.

## Open questions

- **`libcuda.so.1` as a literal SONAME has no NVIDIA documentation behind it.** What is documented
  is that the driver installs `/usr/lib/libcuda.so.<driver version>` with an `ldconfig` symlink,
  and the post's own lab observes `libcuda.so.1` as the string PyTorch's binaries actually request.
  Those two together are the evidence; no NVIDIA page prints `libcuda.so.1`.
- **NVIDIA's docs spell the driver library three different ways** — `cuda.so`, `libcuda.so`,
  `libcuda.so.*`. Unresolved; the post uses the form that matches the installed filename.
- **The effective date of the `-cuNN` suffix retirement is unknown.** Only the current state was
  established. The post does not date the change.
- **Which cuBLAS branch a default FP32 matmul takes** cannot be answered by reading source; it is
  a run-time heuristic. The post says so rather than guessing.
- **DBLP and Semantic Scholar were unreachable** during the scholarly sweep — DBLP behind a bot
  challenge on every mirror, Semantic Scholar returning HTTP 429. Venue checks were triangulated
  across Crossref, arXiv and Google Scholar instead. A future part needing a DBLP citation must
  open it by hand.
- **Windows and aarch64 were not checked.** Every filename and size in this post is Linux x86_64.
- **The two largest libraries in the torch wheel are skipped by the lab's ELF reader**, because
  their dynamic section sits hundreds of megabytes into the file. The scripts say so rather than
  quietly omitting them.
