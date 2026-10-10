---
title: "What the NVIDIA Stack Actually Is"
slug: "what-the-nvidia-stack-actually-is"
date: 2026-09-23
updated: 2026-09-23
summary: "There is no single artifact called CUDA. It is a driver, a runtime, a compiler and a library portfolio, shipped separately — and only one of them must come from your machine."
tags: [machine-learning, cuda, nvidia, gpu, pytorch, packaging]
category: "machine-learning"
series: nvidia-stack
series_position: 1
tier: L2
difficulty: beginner
prerequisites: [python, linux-shell]
reading_minutes: 18
cover_image: "https://minio.canery.in/media/cover-what-the-nvidia-stack-actually-is.png"
canonical_url: "https://canery.in/blogs/what-the-nvidia-stack-actually-is"
---
![A layered map of the NVIDIA software stack from kernel driver up to serving products](https://minio.canery.in/media/cover-what-the-nvidia-stack-actually-is.png)

> [!NOTE]
> **Insights** — There is no single artifact called CUDA. The name covers a kernel driver, a user-mode driver library, a runtime, a compiler toolchain and a portfolio of math libraries, each built and shipped on its own schedule. Exactly one of them has to come from your machine: `libcuda.so.1`, installed by the NVIDIA driver. Everything else — including the library that actually multiplies your matrices — arrives in Python wheels and is assembled by the dynamic loader the moment you `import torch`.

**Level:** beginner · **You need:** Python, a shell · **Time:** ~18 min

> [!TIP]
> **Runnable lab, no GPU required:** every command and every number in this post was produced on a laptop with no NVIDIA GPU, no driver and no CUDA Toolkit installed. The scripts are under [Lab downloads](#lab-downloads) and need nothing but `python3` and a network connection.

## Why this matters

You type `pip install torch`. Several gigabytes land in your virtualenv. Then a colleague asks whether the box needs the CUDA Toolkit, and you find you cannot answer — not because the answer is hard, but because nobody ever told you what the Toolkit *is* relative to the thing pip just installed.

So you run `nvidia-smi`, which prints a CUDA version. Then `nvcc --version`, which prints a different one. Both look authoritative. Neither is wrong. The next part of this series is entirely about why those two numbers differ; this one is about the prior question, which nobody answers first: what are the pieces, and who ships each one?

Getting that map wrong is expensive later. Almost every hard failure in this stack — a launch error, a missing symbol, a library the loader cannot find — is diagnosed at the wrong layer by someone who never had the map. You end up rebuilding PyTorch because a driver was old, or installing a 4 GB Toolkit because a Python package could not find a 800 KB library.

## The problem: five different things are called "CUDA"

When someone says "we're on CUDA 13", they could mean any of five separately built, separately versioned, separately shipped artifacts. Here they are, with the file each one actually puts on disk.

**The kernel modules.** `nvidia.ko` and friends, compiled against your running kernel. These are the only components that talk to the hardware.

**The user-mode driver.** `libcuda.so.1`, installed by the driver package at a path stamped with the driver's own version. It exposes the CUDA driver API, and everything above it is built on that API.

**The CUDA runtime.** `libcudart.so.13`, the library your framework's compiled code actually calls. It belongs to the Toolkit, not to the driver.

**The Toolkit.** A development environment: `nvcc`, headers, the math libraries, the debuggers and profilers. It is a separate product from the driver, and since CUDA 13.4 on Linux the two are versioned and installed independently.

**The libraries.** cuBLAS, cuDNN, NCCL and the rest — the code that performs the arithmetic. Some ship inside the Toolkit, some as their own downloads, some as their own Python packages.

Figure 1 puts them in order, with the artifact and the shipper for each.

![Seven stacked layers from kernel modules up to serving products, each labelled with its file on disk and the product that ships it](https://minio.canery.in/media/fig-01-layer-map-what-the-nvidia-stack-actually-is.png)
*Figure 1. The stack, bottom to top. Read the right-hand column first: the layers are shipped by four different things on four different schedules.*

What makes this genuinely hard, rather than merely tedious, is that none of the five announces which one you are looking at. The same word appears in the driver's output, the compiler's output, a pip package name and a container tag. The numbers attached to it are not the same number, and no error message tells you which layer it came from.

None of this was designed in one sitting. GPUs were programmed through graphics APIs until a unified architecture and a C-like programming model for it arrived together in 2007 and 2008.  Everything above that base was added later, by different teams on different release schedules, which is why the seams sit where they do. Parts of the result are still opaque enough that researchers recover their behavior by microbenchmarking rather than by reading a manual.

The rest of this post replaces that one word with seven artifacts you can point at.

## Worked example: one line of PyTorch, all the way down

Here is the whole program.

```python
import torch

a = torch.randn(4096, 4096, device="cuda")
w = torch.randn(4096, 4096, device="cuda")
c = a @ w
```

Three lines, one matrix multiply. Following `a @ w` downward names every layer in the stack, and every step below was read from PyTorch's source at release tag `v2.14.0`.

**1. Python resolves the operator.** `@` becomes `torch.matmul`, which for two 2-D tensors becomes the ATen operator `aten::mm`. ATen is PyTorch's C++ tensor library — the layer where Python stops and compiled code begins.

**2. A declaration file says what `mm` is.** `mm` is declared in `native_functions.yaml` as a structured delegate to `mm.out`. That file is not documentation; PyTorch's build turns it into the dispatcher's tables.

**3. The dispatcher picks a backend.** Tensors carry a dispatch key. Because these live on the GPU, the key selects the CUDA implementation rather than the CPU one.

**4. The CUDA implementation runs.** `TORCH_IMPL_FUNC(mm_out_cuda)` in `aten/src/ATen/native/cuda/Blas.cpp`.

**5. It forwards to a shared helper.** `mm_out_cuda` calls `addmm_out_cuda_impl`, which reaches `at::cuda::blas::gemm<float>`. GEMM — general matrix multiply — is the BLAS name for this operation, and this wrapper is the last code in the descent that is still PyTorch's.

**6. PyTorch chooses a cuBLAS flavor at run time.** `gemm_internal<float>` branches on a preferred-backend setting.

**7. A vendor library call is made.** The classic path calls `cublasSgemm`. The cuBLASLt path calls `cublasLtMatmulAlgoGetHeuristic` to *ask the library which algorithm to use*, then `cublasLtMatmul`.

**8. The loader finds that symbol.** `cublasSgemm` lives in `libcublas.so.13`, which is not inside the PyTorch wheel. The wheel's libraries carry a search path pointing at `site-packages/nvidia/cu13/lib`, and that is where it is found.

**9. cuBLAS reaches the hardware.** It calls the CUDA runtime, `libcudart.so.13`, which calls the driver library `libcuda.so.1`, which issues `ioctl` calls to the kernel module.

Figure 2 lays the nine steps out with the artifact that owns each one.

![A vertical trace of nine steps from a Python matrix multiply down to a kernel-module ioctl, each step labelled with its owning artifact](https://minio.canery.in/media/fig-02-traced-call-what-the-nvidia-stack-actually-is.png)
*Figure 2. Nine steps, four vendors, and one boundary — step 7 — where your code stops and NVIDIA's begins.*

Now the honest part. You cannot name the GPU kernel that runs. Step 6 is a run-time branch, and on the cuBLASLt path step 7 literally asks the library to pick an algorithm by heuristic. Which machine code executes is decided inside cuBLAS, at the moment of the call.

That is a property of the stack, not a gap in this post. It is also the first useful thing the map buys you: when this matmul is slower than you expected, the question is not "why is PyTorch slow" but "which of these nine steps am I asking about".

## Intuition: nothing installs this stack

Here is the model to carry away. **Your CUDA installation is not installed. It is assembled, by the dynamic loader, every time you `import torch`.**

The evidence is stamped into PyTorch's own binaries. Every compiled library in the wheel carries an `RPATH` — a list of directories the loader searches before the system ones:

```text
$ORIGIN/../../nvidia/cudnn/lib
$ORIGIN/../../nvidia/nvshmem/lib
$ORIGIN/../../nvidia/nccl/lib
$ORIGIN/../../nvidia/cusparselt/lib
$ORIGIN/../../nvidia/cu13/lib
$ORIGIN
```

`$ORIGIN` means "the directory this library is in", so all of these resolve to sibling folders inside `site-packages`.  PyTorch is not looking for CUDA in `/usr/local/cuda`. It is looking for a set of independently downloaded Python packages that happen to be installed next to it, and it stitches them together at import time.

Figure 3 shows the three channels that can deliver these layers and where they overlap.

![A matrix of three supply channels against the stack's layers, showing which channel covers which layer](https://minio.canery.in/media/fig-03-supply-channels-what-the-nvidia-stack-actually-is.png)
*Figure 3. Three ways to get the same layers. Only the leftmost column can deliver the bottom two, and only the bottom two are mandatory.*

It is tempting to say this is just dependency resolution, the way any package manager works. That analogy holds for about one sentence, and then it breaks in two places. First, resolution happens twice: once when pip picks versions, and again — by different rules, against filenames rather than package names — when the loader resolves `libcublas.so.13`. Second, and more importantly, the one library at the bottom of every chain is not in the package set at all. `libcuda.so.1` is named by PyTorch's binaries and shipped by no wheel.  pip cannot deliver it, and nothing in your virtualenv can substitute for it.

That is the whole shape of the stack in one sentence: **everything above the driver is negotiable, and the driver is not.**

## What does the driver actually give you?

Everything above this layer can arrive in a Python wheel. This one cannot: the NVIDIA driver is required for every use of the GPU, display included, and the rest of the CUDA platform is built on it.

On Linux it is not one module but five: `nvidia.ko`, `nvidia-modeset.ko`, `nvidia-uvm.ko`, `nvidia-drm.ko` and `nvidia-peermem.ko`.  Two of them carry the compute path: `nvidia.ko` and `nvidia-uvm.ko`.  `nvidia-uvm.ko` provides the CPU–GPU shared memory CUDA uses, and it generally loads when a CUDA program starts.  `nvidia-modeset.ko` programs the display engine and is not on that path.  `nvidia-peermem.ko` serves remote direct memory access (RDMA) from a network adapter straight into GPU memory.

Those modules ship in two mutually exclusive flavors: open, dual-licensed MIT/GPLv2 and published on GitHub with each release, and proprietary.  The user-space components are identical either way.  So the flavor is a licensing and hardware-support question, not a behavioral one — the proprietary modules cover Turing through Hopper, and Blackwell and later are open-module-only.

One installer puts two very different kinds of thing on the machine; the diagram splits them into kernel modules and driver-installed user-space libraries.

![Two-column diagram: on the left, five NVIDIA kernel modules, with nvidia.ko and nvidia-uvm.ko marked as the compute path; on the right, the user-space libraries the same driver installs — libcuda.so, libnvidia-ml.so and libnvidia-ptxjitcompiler.so — each filename ending in the driver version](https://minio.canery.in/media/fig-04-driver-contents-what-the-nvidia-stack-actually-is.png)
*Figure 4. Both columns come out of the same driver package, and only the left one is kernel code.*

The right column is the half most readers have never thought about. `libcuda.so` is installed by the display driver, not by the Toolkit, at `/usr/lib/libcuda.so.<driver version>` with an `ldconfig` symlink beside it.  That file is the user-mode driver: the shared library that exposes the driver API, the low-level entry point the CUDA runtime is built on top of.  Your framework's binaries name `libcuda.so.1`, and no wheel ships it.  It comes from the host driver, always.

Two more files land the same way. `libnvidia-ml.so.<driver version>` is the NVIDIA Management Library (NVML), the driver's own library for reading device state.  `nvidia-smi` is a program built on it.  Read NVML when you write tooling: `nvidia-smi` output carries no backward-compatibility guarantee, while NVML's bindings do.  The PTX JIT compiler is a driver artifact too, installed as `libnvidia-ptxjitcompiler.so.<driver version>`.  The driver README lists these files with the driver version baked into each name.

The `nvidia-smi` manual now marks its `CUDA Version` field deprecated in favor of `CUDA UMD Version`, defined as the CUDA user-mode driver version.  The new label names the artifact the number came from.

## What is in the CUDA Toolkit, and do you need it?

Four kinds of thing sit inside that development environment — the compiler toolchain, the runtime, the accelerated libraries and the tools.

The compiler toolchain turns GPU source into something the hardware can execute. The CUDA runtime is one of the libraries the Toolkit provides, and it is the API your own code calls to allocate memory and launch work.  The accelerated libraries are prebuilt math you would otherwise write yourself: cuBLAS, cuFFT, cuRAND, cuSOLVER, cuSPARSE.  The tools are the ones later parts of this series lean on: `cuobjdump` prints what is inside a compiled GPU binary, Compute Sanitizer checks a running GPU program for correctness bugs, `cuda-gdb` debugs code while it runs on the GPU, and Nsight Systems and Nsight Compute are the measurement pair.  On Linux the whole set installs to `/usr/local/cuda-<version>`, with a `/usr/local/cuda` symlink aimed at it.

`nvcc` is the program you invoke to compile CUDA source, and its name misleads. It is a toolchain, not a single compiler. It splits device code — the part that runs on the GPU — from the host code that runs on the CPU, hands each to its own compiler, and drives several other programs along the way: `cudafe++`, `ptxas`, `nvlink` and `fatbinary` among them.  You do not have to take that on faith. Compile with `nvcc -v` and it prints every tool invocation in the workflow. Add `-keep` and it leaves the intermediates on disk for you to open.

Two facts settle whether you need any of this. The CUDA runtime links statically by default — `nvcc` links `libcudart_static` unless you pass `--cudart=shared` — so a binary built that way already carries its runtime.  And NVIDIA documents its CUDA pip wheels as runtime-only, with the developer tools left out.  The two are genuinely separate artifacts, not one shipped in halves: `libcudart.so.13` names no driver library in its dynamic section and imports none of its symbols.  That is a fact about *linking*, not about *calling* — step 9 of the trace still happens. The runtime looks the driver up by name once the process is running, rather than being bound to it when it was built, which is exactly why the runtime can travel inside a wheel and the driver cannot. The rule falls out of the pair: you need the Toolkit to build device code, and you do not need it to run someone else’s. The building already happened on somebody else’s machine, and what pip hands you is its output.

One more detail finishes off the “one version” model — the components of a single Toolkit release, each beside the version number it actually carries.

![Table of the nine component wheels inside CUDA Toolkit release 13.0.3, each beside its own version: nvidia-cublas 13.1.1.3, nvidia-npp 13.0.1.2, nvidia-cuda-runtime 13.0.96, nvidia-cuda-nvcc 13.0.88, nvidia-nvtx 13.0.85, nvidia-cusparse 12.6.3.3, nvidia-cusolver 12.0.4.66, nvidia-cufft 12.0.0.61 and nvidia-curand 10.4.0.35](https://minio.canery.in/media/fig-05-toolkit-versions-what-the-nvidia-stack-actually-is.png)
*Figure 5. Notice that no component’s version matches the release it shipped in, and no two of them agree.*

Every component carries its own version number rather than the Toolkit’s.  Read down the right-hand column for `cuda-toolkit==13.0.3`: cuBLAS is 13.1.1.3, cuFFT is 12.0.0.61, cuRAND is 10.4.0.35, cuSOLVER is 12.0.4.66, cuSPARSE is 12.6.3.3.  One release, one install directory, and not one of those numbers is the release number.  So “I have CUDA 13” names a box, not its contents.  What those numbers mean for compatibility is part 2.

## What is CUDA-X, and which of it are you already using?

Look for CUDA-X on disk and you will not find it.  It is a portfolio label — a grouping NVIDIA puts over its GPU-accelerated libraries — and no artifact carries the name.  There is no `libcudax.so`, no CUDA-X version, nothing to download called CUDA-X.  The clearest evidence comes from NVIDIA itself: the CUDA Libraries reference hub, where the API manuals for these libraries live, never uses the term.

There is a sharper tell. NVIDIA’s two CUDA-X pages do not list the same members.  Treat any CUDA-X list as a snapshot, not a specification you can check an install against.

The libraries under the label are real, and figure 6 groups them by how each one reaches your machine.

![A dashed CUDA-X label drawn around two rows of libraries: an upper row that ships inside the CUDA Toolkit — cuBLAS, cuFFT, cuSOLVER, cuSPARSE — and a lower row that is a separate download or its own wheel — cuDNN, NCCL, cuSPARSELt — with a dashed arrow from cuDNN up to cuBLAS](https://minio.canery.in/media/fig-06-cuda-x-label-what-the-nvidia-stack-actually-is.png)
*Figure 6. The label spans both rows, so it tells you nothing about where a library comes from; the row underneath it does.*

Three libraries under that label do most of your work, and figure 6 shows they do not all arrive the same way. cuBLAS, the CUDA Basic Linear Algebra Subprograms library, is the dense linear-algebra implementation that runs the matrix multiply traced earlier in this post; it sits in the figure’s upper row because it ships inside the Toolkit as well as in its own wheel.  Care about it any time your model runs a linear layer. cuDNN, the CUDA Deep Neural Network library, holds the hand-tuned primitives for convolution and the attention building blocks, and its current wheel ships 10 libraries totalling 887.7 MB.  Care about it the moment your model has a convolution or an attention layer, because that library runs them, not your framework. NCCL, the NVIDIA Collective Communications Library, ships `libnccl.so.2` at 343.9 MB and runs the collectives that exchange gradients between GPUs, so it matters the moment a second GPU appears — a later part of this series covers what changes then.

Neither cuBLAS nor cuDNN is inside the `torch` wheel.  All three ship as their own packages, and `nvidia-cudnn-cu13` and `nvidia-nccl-cu13` are live and maintained.  cuDNN lands in your virtualenv anyway, resolved as a dependency rather than chosen by you.

cuBLAS sits one step further down that chain, and PyTorch does ask for it — just not anywhere you would think to look. It is the word `cublas` inside a bracket, one of eleven extras on a meta-package: `cuda-toolkit[cublas,…]`.  That is why it appears in no list of packages named `nvidia-something`, and in nothing PyPI’s summary endpoint returns. It arrives a second time as well: `nvidia-cudnn-cu13` depends on `nvidia-cublas` directly, so cuBLAS would land even if that extra were dropped.  It is not small either. In the build current today, `libcublas.so.13` is 57.6 MB and `libcublasLt.so.13` is 545.5 MB.  That second file is larger than `libtorch_cuda.so` at 502.8 MB.  The biggest single file in a PyTorch GPU install is NVIDIA’s matrix-multiply library, and nothing you installed named it.

## Installer, wheel, or container: which do you need?

Pick the channel from your task, not from the vendor’s product page.

| Your task                                      | What you need                                                  | What you do not         |
| ---------------------------------------------- | -------------------------------------------------------------- | ----------------------- |
| Run someone else’s model                      | A host driver, plus the framework’s own wheels                | The Toolkit             |
| Build a C++/CUDA extension against a framework | The Toolkit, plus that framework’s headers                    | A second driver install |
| Compile a standalone kernel                    | The Toolkit                                                    | Any framework           |
| Ship to a machine you do not control           | A container image, plus a driver on that host                  | A Toolkit on that host  |
| Use the profilers                              | The Toolkit installer, because the pip wheels are runtime-only | The pip wheels          |

Most readers arrive on the pip channel, so trace what it resolves to. NVIDIA publishes a meta-package on PyPI literally named `cuda-toolkit` that contains no software.  It only pulls in component wheels selected by extras, the `name[a,b]` syntax that picks optional dependency groups.  PyTorch uses exactly that mechanism and names eleven components.  Here are the CUDA dependencies the torch 2.14.0 wheel declares in its own `METADATA`.

```text
cuda-toolkit[cublas,cudart,cufft,cufile,cupti,curand,cusolver,cusparse,nvjitlink,nvrtc,nvtx]==13.0.3
nvidia-cudnn-cu13
nvidia-cusparselt-cu13
nvidia-nccl-cu13
nvidia-nvshmem-cu13
```

Two naming schemes are live at once. Both resolve, so check which one you are reading.  With CUDA 13 the component wheels dropped the CUDA major-version suffix: `nvidia-cuda-runtime` replaces `nvidia-cuda-runtime-cu12`.  The `-cu13` spellings became deprecated placeholders that install and do nothing. `nvidia-cublas-cu13` is version 0.0.1, with the summary “DEPRECATED: Use nvidia-cublas instead”.  The suffix did not disappear everywhere. `nvidia-cudnn-cu13`, `nvidia-nccl-cu13`, `nvidia-cusparselt-cu13` and `nvidia-nvshmem-cu13` stay suffixed and maintained, which is why both spellings sit in the block above.

Resolving that line gives the graph below, where two nodes sit outside the virtualenv.

![Dependency graph of pip install torch: a site-packages box holding torch, the cuda-toolkit meta-package, its eleven component wheels, nvidia-cudnn-cu13 and nvidia-cublas, beside a separate host box holding libcuda.so.1 and the nvidia.ko kernel module](https://minio.canery.in/media/fig-07-resolved-graph-what-the-nvidia-stack-actually-is.png)
*Figure 7. Every box inside `site-packages` arrives in a wheel. The two on the right cannot: `libcuda.so.1`, and the kernel module behind it, come from the host.*

Inside that box sit 32 packages and 90 shared libraries.  The two nodes outside it are the decision rule in a picture.

A container moves the boxes without moving that line. NVIDIA's CUDA images are built as a chain — `devel` starts `FROM` the `runtime` image, `runtime` `FROM` `base`, and `base` from a plain distribution image — and not one installs a driver. It declares one on the *host* instead, through `NVIDIA_REQUIRE_CUDA`.  The devel image points `LIBRARY_PATH` at `/usr/local/cuda/lib64/stubs`, so code that runs on the GPU can link inside a container with no driver present.  What the container runtime injects from the host is driver-owned only: `nvidia-smi`, `libcuda`, `libnvidia-ml` and friends.  No Toolkit library is ever injected.

## Implementation: read the stack before you install it

Every number in this post came off a machine with no NVIDIA GPU, no driver and no CUDA Toolkit. You need none of them either. Three read-only inspections tell you what a framework will ask the operating system for.

### Can you list a wheel without downloading it?

A zip keeps its index — the central directory — at the end of the file, so a client that can request byte ranges reads the listing and skips the payload.  `inspect_wheel.py` does that with Python's `zipfile` over a Range-capable server.

```bash
python3 inspect_wheel.py torch 2.14.0
```

```text
package        torch 2.14.0
wheel          torch-2.14.0-cp312-cp312-manylinux_2_28_x86_64.whl
download size  554.6 MB
entries        13,043
unpacked size  1144.2 MB
cost to list   3 HTTP range requests, 1.2 MB transferred
```

Three range requests and 1.23 MB on the wire list all 13,043 entries of a 554.6 MB archive.  Thirteen of those entries are shared libraries, and not one is cuBLAS.

### Whose metadata are you reading?

The same run prints the `METADATA` file from inside the wheel rather than PyPI's JSON endpoint. Both describe one artifact, and the wheel is the copy an installer actually consumes, so it is the one that settles a dependency question.

```text
Requires-Dist: cuda-toolkit[cublas,cudart,cufft,cufile,cupti,curand,cusolver,cusparse,nvjitlink,nvrtc,nvtx]==13.0.3
```

One line, eleven CUDA components requested as extras, pinned at 13.0.3.  Four `nvidia-*` packages follow it.

### What will the loader be asked for?

Linux binaries use ELF, the Executable and Linkable Format, and every ELF library carries a dynamic section. `DT_NEEDED` is an entry there naming one library this binary needs at load time; `DT_RPATH` holds the `$ORIGIN` search list you saw earlier. Read both to see whether a dependency travels inside the wheel or has to come from the host. `inspect_wheel.py` prints them for every library in the wheel.

```bash
python3 inspect_wheel.py torch 2.14.0
```

```text
  libtorch_cuda_linalg.so  (SONAME libtorch_cuda_linalg.so)
      NEEDED   libtorch_cuda.so
      NEEDED   libcusolver.so.12
      NEEDED   libc10_cuda.so
      NEEDED   libcudart.so.13
      NEEDED   libtorch_cpu.so
      NEEDED   libc10.so
      NEEDED   libpthread.so.0
      NEEDED   libcublas.so.13
      NEEDED   libcusparse.so.12
      ...  and libstdc++, libm, libgcc_s, libc, ld-linux
      RPATH    $ORIGIN/../../nvidia/cudnn/lib
      RPATH    $ORIGIN/../../nvidia/nvshmem/lib
      RPATH    $ORIGIN/../../nvidia/nccl/lib
      RPATH    $ORIGIN/../../nvidia/cusparselt/lib
      RPATH    $ORIGIN/../../nvidia/cu13/lib
      RPATH    $ORIGIN
```

That is one library of the thirteen, with the five C-runtime entries elided.

This binary asks for cuBLAS, cuSOLVER, cuSPARSE and the CUDA runtime, and the torch wheel ships none of them — the `RPATH` lines are where the loader goes to find them.  The number after `.so` is that library's major version: cuBLAS asks for 13, cuSOLVER for 12, and none of those numbers is “the CUDA version”; part 2 explains why.

Runnable versions of `inspect_wheel.py` and `resolve_stack.py` are in [Lab downloads](https://minio.canery.in/media/lab-what-the-nvidia-stack-actually-is.zip). They need python3 and a network connection, nothing else.

## Limitations and common mistakes

> [!WARNING]
> **The common mistake: filtering a dependency list on the prefix `nvidia-`.** Do it to `torch`'s requirements and four packages come back — cuDNN, NCCL, cuSPARSELt, nvSHMEM — and you conclude PyTorch no longer depends on cuBLAS or the CUDA runtime. It does. Both arrive through `cuda-toolkit[cublas,cudart,...]`, a name matching neither prefix, with the components hidden inside a bracket.  Two independent passes of the research for this post made that error. The fix is one habit: read the whole `Requires-Dist` block out of the wheel's own `METADATA`, because the archive is what an installer consumes.

**Do not read `nvidia-smi`'s CUDA number as "the CUDA version installed".** It reports a property of the user-mode driver, which is why the manual now labels that field `CUDA UMD Version`.  What each of those numbers promises is the next part's subject.

**Do not assume a container image carries a driver.** No image in NVIDIA's CUDA chain installs one; `base` declares a host driver requirement instead.  The driver comes from the host and is injected at run time, which is also why no Toolkit library is ever injected.

**Do not assume the names in this post are stable.** The wheels dropped their `-cuNN` suffix at CUDA 13 — inconsistently, so both schemes are live.  The Toolkit stopped shipping the driver at 13.4.  The shape of the stack is durable; the names on the boxes are not, and anything you read about this stack more than a year old should be checked against the artifact rather than believed.

## Key takeaways

- No single artifact is called CUDA. The word covers a kernel driver, a user-mode driver library, a runtime, a compiler toolchain and a library portfolio, shipped by four different products on four schedules.
- Only the driver must come from the host. `libcuda.so.1` is named by your framework's binaries and shipped by no Python wheel, ever.
- Nothing installs the rest of the stack — the dynamic loader assembles it inside `site-packages` at import time, following an `RPATH` baked into the framework's libraries.
- You need the CUDA Toolkit to build device code, not to run someone else's. The pip wheels are runtime-only by NVIDIA's own statement.
- CUDA-X is a label, not an artifact, and you are already using several of the libraries it covers — cuBLAS reaches your virtualenv as the `cublas` extra of a meta-package, under a name PyTorch never spells out.

## Try it yourself

Each of these runs on a machine with no GPU.

**1.** Before running anything, predict how many `.so` files ship inside a CUDA-enabled PyTorch wheel, and whether cuBLAS is one of them. Then check.

<details><summary>Answer</summary>

Thirteen, and no. The wheel ships `libtorch_cuda.so`, `libtorch_cpu.so` and eleven smaller libraries; no cuBLAS, cuDNN, cudart, cuFFT, cuSOLVER, cuRAND or cuSPARSE library is inside it.  The two largest are 502.8 MB and 446.3 MB of a 554.6 MB download.

</details>

**2.** Find one library your framework's binaries require that no package in its dependency graph provides.

<details><summary>Answer</summary>

`libcuda.so.1`, requested by `libcaffe2_nvrtc.so`. Every other requested library resolves to a wheel or to glibc. This one resolves to the host driver, which is the entire argument of this post — and it is why a container image needs no driver but a container *host* does.

</details>

**3.** `pip install nvidia-cublas-cu13` succeeds and gives you no cuBLAS. Why?

<details><summary>Answer</summary>

Because `nvidia-cublas-cu13` is one of the 0.0.1 placeholders left behind when the component wheels dropped their `-cuNN` suffix.  The install succeeds, installs nothing, and reports no error. The name you want is `nvidia-cublas` — but cuDNN, NCCL and cuSPARSELt kept their suffixes, so the rule does not apply uniformly.

</details>

## References

### Lab downloads

- [`README.md`](LAB_01) — prerequisites, run order, expected results, and the caveats that matter.
- [`wheelio.py`](LAB_02) — shared helpers: PyPI metadata, a seekable HTTP Range file, and a minimal ELF64 dynamic-section reader.
- [`inspect_wheel.py`](LAB_03) — lists a wheel's contents without downloading it and prints the `SONAME`, `DT_NEEDED` and `DT_RPATH` of every library it ships.
- [`resolve_stack.py`](LAB_04) — walks the declared dependency graph and maps every requested library to the wheel that provides it, or to the host driver.
- [`expected-output.txt`](LAB_05) — both runs captured on 2026-09-23, to diff your own against.
- Lab Download Link: [experiment-lab](https://minio.canery.in/media/lab-what-the-nvidia-stack-actually-is.zip)

### Sources

**Papers**

- Owens, Luebke, Govindaraju, Harris, Krüger, Lefohn and Purcell, "A Survey of General-Purpose Computation on Graphics Hardware", *Computer Graphics Forum* 26(1), 2007. [doi:10.1111/j.1467-8659.2007.01012.x](https://doi.org/10.1111/j.1467-8659.2007.01012.x)
- Lindholm, Nickolls, Oberman and Montrym, "NVIDIA Tesla: A Unified Graphics and Computing Architecture", *IEEE Micro* 28(2), 2008. [doi:10.1109/MM.2008.31](https://doi.org/10.1109/MM.2008.31)
- Nickolls, Buck, Garland and Skadron, "Scalable Parallel Programming with CUDA", *ACM Queue* 6(2), 2008. [doi:10.1145/1365490.1365500](https://doi.org/10.1145/1365490.1365500)
- Jia, Maggioni, Staiger and Scarpazza, "Dissecting the NVIDIA Volta GPU Architecture via Microbenchmarking", 2018. [arXiv:1804.06826](https://arxiv.org/abs/1804.06826) — a preprint, cited here only as evidence that parts of this stack are undocumented enough to require reverse engineering.

**Specifications**

- Python Packaging Authority, [Binary distribution format](https://packaging.python.org/en/latest/specifications/binary-distribution-format/) — the wheel format the lab reads. Accessed 2026-09-22.
- Python Packaging Authority, [Dependency specifiers](https://packaging.python.org/en/latest/specifications/dependency-specifiers/) — the extras syntax behind `cuda-toolkit[cublas,...]`. Accessed 2026-09-22.
- [`ld.so(8)`](https://man7.org/linux/man-pages/man8/ld.so.8.html) — `RPATH` and `RUNPATH` search order. Accessed 2026-09-22.

**NVIDIA documentation** — all accessed 2026-09-22

- [CUDA C++ Programming Guide — The CUDA platform](https://docs.nvidia.com/cuda/cuda-programming-guide/01-introduction/cuda-platform.html)
- [CUDA C++ Programming Guide — NVCC: The NVIDIA CUDA Compiler](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/nvcc.html)
- [CUDA Driver API — Difference between the driver and runtime APIs](https://docs.nvidia.com/cuda/cuda-driver-api/driver-vs-runtime-api.html)
- [CUDA Toolkit Release Notes](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html) — the component table and its per-component versions
- [CUDA Installation Guide for Linux](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html) — the pip, conda and package-manager channels
- [NVIDIA Linux driver README — Installed Components](https://us.download.nvidia.com/XFree86/Linux-x86_64/615.71.09/README/installedcomponents.html)
- [NVIDIA Linux driver README — Open Linux Kernel Modules](https://us.download.nvidia.com/XFree86/Linux-x86_64/615.71.09/README/kernel_open.html)
- [NVML API Reference](https://docs.nvidia.com/deploy/nvml-api/index.html) and the [`nvidia-smi` manual](https://docs.nvidia.com/deploy/nvidia-smi/index.html)
- [CUDA-X](https://www.nvidia.com/en-us/technologies/cuda-x/), the [GPU-Accelerated Libraries index](https://developer.nvidia.com/gpu-accelerated-libraries), and the [CUDA Libraries documentation hub](https://docs.nvidia.com/cuda-libraries/index.html)
- [NVIDIA Container Toolkit — Architecture Overview](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/arch-overview.html)
- [CUDA Binary Utilities](https://docs.nvidia.com/cuda/cuda-binary-utilities/index.html) and [Compute Sanitizer](https://docs.nvidia.com/compute-sanitizer/ComputeSanitizer/index.html)

**Primary implementation evidence** — accessed 2026-09-22 and 2026-09-23

- [NVIDIA/open-gpu-kernel-modules](https://github.com/NVIDIA/open-gpu-kernel-modules) — the open kernel modules and their README
- [libnvidia-container `src/nvc_info.c`](https://github.com/NVIDIA/libnvidia-container/blob/24a848d9f0f31a40d047a8178b86eb024548546e/src/nvc_info.c) — the exact host files injected into a container
- PyTorch at tag `v2.14.0`: [`native_functions.yaml`](https://github.com/pytorch/pytorch/blob/v2.14.0/aten/src/ATen/native/native_functions.yaml), [`native/cuda/Blas.cpp`](https://github.com/pytorch/pytorch/blob/v2.14.0/aten/src/ATen/native/cuda/Blas.cpp), [`cuda/CUDABlas.cpp`](https://github.com/pytorch/pytorch/blob/v2.14.0/aten/src/ATen/cuda/CUDABlas.cpp)
- [`torch` 2.14.0 on PyPI](https://pypi.org/project/torch/2.14.0/) — the wheel, its `METADATA` and its ELF dynamic sections, inspected with the lab scripts
- [`cuda-toolkit`](https://pypi.org/project/cuda-toolkit/), [`nvidia-cublas`](https://pypi.org/project/nvidia-cublas/) and [`nvidia-cuda-runtime`](https://pypi.org/project/nvidia-cuda-runtime/) on PyPI
- [NVIDIA CUDA container images](https://gitlab.com/nvidia/container-images/cuda) — the `base`, `runtime` and `devel` Dockerfiles
