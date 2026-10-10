---
title: "CUDA Architecture Repairs: PyTorch, TensorRT-LLM, ONNX"
slug: "architecture-aware-tensorrt-llm-cuda-onnx"
date: 2026-09-15
updated: 2026-09-22
summary: "Diagnose CUDA architecture mismatches, rebuild only the broken binary layer, and deploy transformer inference through TensorRT-LLM or ONNX safely in production."
tags: [machine-learning, cuda, pytorch, tensorrt-llm, onnx, cmake]
category: "machine-learning"
series: nvidia-stack
series_position: 6
tier: L4
difficulty: advanced
prerequisites: [linux, python, cmake, docker, transformer-basics]
reading_minutes: 40
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/architecture-aware-tensorrt-llm-cuda-onnx"
---

![A layered CUDA inference stack connecting GPU architecture, PyTorch, TensorRT-LLM, and ONNX](COVER)

> [!NOTE]
> **Insights** — Rebuild the lowest layer that is actually missing code for your GPU: one CUDA extension, PyTorch itself, or TensorRT-LLM. Compute capability, CUDA Toolkit release, PyTorch binary coverage, model support, and product validation are separate facts. TensorRT-LLM 1.2 loads supported Hugging Face checkpoints through its PyTorch backend; ONNX is a sibling route into TensorRT or ONNX Runtime, not a required stage before TensorRT-LLM.

**Level:** advanced · **You need:** Linux shell, Python environments, CMake, Docker, and transformer basics · **Time:** ~40 minutes

> [!TIP]
> **Runnable lab:** The audit scripts, CUDA and extension probes, model inspection, ONNX path, TensorRT-LLM generation, and benchmark harness are listed under [Lab downloads](#lab-downloads) at the end. Use them when you want to reproduce the checks; the explanation remains in this article. Commands below call the directory holding those files `lab/`, keeping the `cuda_probe/` and `extension_probe/` subdirectories from their download paths.

## Why this matters

“CUDA is available” is one of the weakest green lights in an inference stack. It proves that PyTorch can see a CUDA driver and at least one device. It does not prove that the installed library contains a compatible kernel image, that your separately compiled extension targets the same GPU, that TensorRT-LLM implements the model class, or that the chosen kernels fit in memory.

That distinction matters at both ends of the hardware lifecycle. An NVIDIA T4 is a compute-capability 7.5 device, written `sm_75` when selecting a real CUDA binary target. A newer NVIDIA GB10 is compute capability 12.1, written `sm_121`. NVIDIA’s [current compute-capability table](https://developer.nvidia.com/cuda/gpus) records both. The T4 may be older than the validated set of a new serving release. The GB10 may be newer than a wheel built before 12.x devices existed. Both machines can surface an “unsupported architecture” symptom, but compiling the same thing on both is the wrong response. <!-- L05 --><!-- L06 --><!-- L68 -->

The stack is layered. Figure 1 shows the evidence required at each boundary.

![Compatibility stack from host and GPU through driver, compiler, binaries, framework, model, and runtime](FIG_01)
*Figure 1. Compatibility is a stack, not a single version comparison. A check at one layer cannot certify the layers above it.*

The useful question is not “does CUDA support this GPU?” It is “which artifact that this process will load lacks a code path compatible with this GPU?” That wording points to the smallest repair.

Figure 2 separates two numbers that are often accidentally compared.

![Two independent axes for CUDA Toolkit releases and GPU compute capabilities](FIG_02)
*Figure 2. `sm_121` identifies a GPU feature level. “CUDA 13.1” identifies a Toolkit release. The selected compiler must know the target, but the numbers do not need to match.*

The [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/01-introduction/cuda-platform.html) defines compute capability as a hardware feature identifier. The Toolkit is software: compiler, headers, libraries, and development tools. The driver is another product again. `nvidia-smi` reports a driver’s CUDA ceiling; `nvcc --version` reports the compiler actually selected on `PATH`. A host can have a suitable driver and no Toolkit at all. <!-- L09 --><!-- L10 --><!-- L11 -->

## The problem: one launch error, two opposite machines

Consider two case files. They are diagnostic scenarios, not fabricated benchmark runs.

**Machine A: NVIDIA T4.** The hardware reports compute capability 7.5. PyTorch can enumerate it. A native extension or older TensorRT-LLM stack may contain `sm_75` code, and a particular model can run. Yet the [TensorRT-LLM 1.2 hardware page](https://nvidia.github.io/TensorRT-LLM/1.2.0/supported-hardware.html) lists selected Blackwell, Hopper, Ada, and Ampere systems and does not list T4. That is a release-validation boundary. It is not a law of physics preventing every TensorRT-LLM instruction from executing on Turing. <!-- L46 -->

**Machine B: a GB10-class `sm_121` device.** The driver sees the device. The selected modern `nvcc` lists `compute_121` and `sm_121`, but an installed, pinned PyTorch build has no compatible 12.x code image. Device discovery may succeed before a real tensor operation forces a missing kernel to launch. In that case the binary is older than the hardware path it must execute.

Figure 3 places those cases side by side.

![T4 and sm121 hosts with similar symptoms but different root causes](FIG_03)
*Figure 3. The T4 case is a product-version and kernel-path question. The `sm_121` case can be a binary-inventory question. Similar errors do not imply the same rebuild.*

Three terms keep the claims honest:

- **Officially validated** means the vendor tested and documents a release on the product or configuration.
- **Executable** means this exact artifact, model, precision, and workload completed on this exact stack.
- **Supported** is a vendor or project policy statement. It may include testing, maintenance, and issue-handling commitments that a one-off successful run cannot establish.

> [!NOTE]
> **T4 field evidence:** the project owner reports having run inference on T4-class smaller-SM hardware. The exact TensorRT-LLM, CUDA, PyTorch, model, and precision tuple was not captured for this article, so the report establishes useful field experience but is not presented as a reproducible TensorRT-LLM 1.2 benchmark.

There is also public historical evidence of the mechanism. An NVIDIA TensorRT-LLM [T4 issue trace from a 0.11 development build](https://github.com/NVIDIA/TensorRT-LLM/issues/1865) records the runtime choosing an unfused multi-head-attention fallback because the fused path did not support the configuration on `sm_75`. That trace does not prove a successful end-to-end run, and it says nothing universal about 1.2. It does disprove the simplistic model in which an unlisted or older SM can never reach a compatible fallback path. <!-- L69 --><!-- L70 -->

The new-device case has an equally important nuance. Do not diagnose it by testing whether the literal string `sm_121` appears in `torch.cuda.get_arch_list()`. CUDA has compatibility rules among baseline, family-specific, and exact architecture targets. Current PyTorch source contains [compatibility-aware checks](https://github.com/pytorch/pytorch/blob/main/torch/cuda/__init__.py), not a strict equality comparison. A compatible `sm_120`, `compute_120`, or family target may cover a 12.1 device, depending on how the artifact was built. The proof is a PyTorch compatibility warning plus a synchronized core CUDA operation—not string inequality. <!-- L23 --><!-- L24 --><!-- L72 -->

A compiled CUDA artifact does not hold one copy of a kernel. It holds an inventory: real machine-code images called **cubins**, each built for one compute capability, and optionally **PTX**, a virtual instruction format the driver can compile at load time. Figure 4 shows why enumeration and execution can disagree.

![CUDA loader choosing exact cubin, compatible image, PTX JIT, or failing](FIG_04)
*Figure 4. The driver first needs a compatible code image. An exact cubin is direct; compatible baseline or family code may also run; PTX may be JIT-compiled when its version and target are acceptable; otherwise launch fails.*

NVIDIA’s [`nvcc` documentation](https://docs.nvidia.com/cuda/cuda-compiler-driver-nvcc/#gpu-compilation) describes how repeated `--generate-code` options create this inventory. At launch, the driver selects something it can execute. `torch.cuda.is_available()` does not inspect every kernel in PyTorch, every out-of-tree extension, or every fused attention plugin. Only the path you invoke exposes what is missing. <!-- L14 --><!-- L15 --><!-- L16 -->

## Worked example: audit before rebuilding

Run the same audit on both machines. Save the output with the incident or benchmark; it is part of the result.

### Step 1: identify the host and device

Start below every framework:

```bash
uname -a
uname -m

nvidia-smi \
  --query-gpu=index,name,uuid,driver_version,compute_cap,memory.total \
  --format=csv,noheader
```

If the installed `nvidia-smi` does not accept `compute_cap`, use the CUDA Runtime, Driver API, NVML, or PyTorch after recording that limitation. NVIDIA documents these [compute-capability query methods](https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/compute-capabilities.html). <!-- L07 --><!-- L08 -->

The CPU architecture matters too. An `x86_64` Python wheel cannot be installed into an `aarch64` environment merely because both hosts contain an NVIDIA GPU. Record `uname -m`, the Python interpreter architecture, and the container image architecture before debugging CUDA code generation.

On Machine A, the expected hardware identity is T4 and 7.5. On Machine B, the expected identity is GB10-class and 12.1. If the result differs, stop: you are targeting a name from an inventory spreadsheet rather than the device assigned to the process.

### Step 2: separate driver from Toolkit

```bash
nvidia-smi

command -v nvcc
nvcc --version
nvcc --list-gpu-arch
nvcc --list-gpu-code
```

The CUDA version printed by `nvidia-smi` is the maximum level exposed by the installed driver, not proof that `/usr/local/cuda` exists. NVIDIA’s [driver/Toolkit matrix](https://docs.nvidia.com/datacenter/tesla/drivers/cuda-toolkit-driver-and-architecture-matrix.html) documents the separation and minimum-driver relationship. If several Toolkits exist, record the resolved `nvcc` path and set `CUDAToolkit_ROOT` or `CUDA_HOME` deliberately. Do not let a shell symlink choose a compiler silently.

`nvcc --list-gpu-arch` prints virtual targets such as `compute_121`; `--list-gpu-code` prints real targets such as `sm_121`. If your selected compiler does not know the requested target, CMake, PyTorch, and TensorRT-LLM cannot force it to generate that target by spelling the number harder. Select a Toolkit that recognizes the SM, or select a different source/runtime path. <!-- L13 -->

For T4, the lifecycle question runs in the other direction: confirm that the chosen new Toolkit still emits the required 7.5 code and that the product source still contains a Turing-capable kernel path. NVIDIA’s architecture matrix warns that Toolkit and driver releases can eventually remove older architecture support. <!-- L12 -->

### Step 3: inspect the installed PyTorch binary

Run a script that records the binary’s build metadata and launches a core operation:

```python
import torch

print("torch:", torch.__version__)
print("built with CUDA:", torch.version.cuda)
print("device available:", torch.cuda.is_available())
print("compiled code images:", torch.cuda.get_arch_list())

for index in range(torch.cuda.device_count()):
    print(index, torch.cuda.get_device_name(index))
    print("device capability:", torch.cuda.get_device_capability(index))
    value = (torch.arange(8, device=index) + 1).sum()
    torch.cuda.synchronize(index)
    print("core CUDA op:", value.item())
```

[`get_device_capability()`](https://docs.pytorch.org/docs/stable/generated/torch.cuda.get_device_capability.html) describes the device. [`get_arch_list()`](https://docs.pytorch.org/docs/stable/generated/torch.cuda.get_arch_list.html) describes code compiled into the library. The synchronized tensor expression proves that PyTorch core actually launched a kernel. The companion `audit_torch.py`, available under [Lab downloads](#lab-downloads), preserves warnings and exceptions as JSON.

Interpret the combinations carefully:

| Device visible | Core operation | Extension | Diagnosis |
|---|---|---|---|
| No | not attempted | not attempted | driver, device assignment, container runtime, or CPU-only PyTorch problem |
| Yes | passes | fails | rebuild or replace that extension first |
| Yes | fails with incompatible/no-kernel warning | not relevant | replace the PyTorch wheel or build PyTorch |
| Yes | passes | passes | move upward to model/runtime/precision/memory diagnosis |

Figure 5 turns the audit into stop conditions.

![Decision tree from host visibility through compiler, PyTorch core, extension, model, and runtime](FIG_05)
*Figure 5. Each passing test moves the investigation upward. Rebuild only after a failing test identifies the artifact that owns the missing kernel.*

Figure 6 focuses on the PyTorch decision.

![Compatibility-aware comparison of device capability, PyTorch code images, warnings, and a synchronized operation](FIG_06)
*Figure 6. The decisive PyTorch test is not `sm_121 in get_arch_list()`. Use the inventory, PyTorch’s compatibility logic, its warning, and a real operation together.*

For Machine B, first check the [PyTorch installation selector](https://pytorch.org/get-started/locally/) for another official wheel of the required PyTorch release built against a CUDA family that covers the device. Current PyTorch diagnostics can even suggest compatible wheel families. Replacing one wheel is cheaper and less risky than compiling the framework. Proceed to a source build only when the application must remain on a revision for which no compatible published build exists and that source revision can be built for the target.

### Step 4: identify the model before loading weights

Do not download gigabytes to discover that the runtime has no adapter for the class. Resolve the configuration first:

```bash
python lab/inspect_model.py \
  TinyLlama/TinyLlama-1.1B-Chat-v1.0 \
  --revision <immutable-commit>
```

Hugging Face [AutoConfig](https://huggingface.co/docs/transformers/model_doc/auto) reveals `model_type`, the declared `architectures`, layer/head counts, and the resolved repository commit. Compare the architecture with TensorRT-LLM’s [release-specific model table](https://nvidia.github.io/TensorRT-LLM/1.2.0/models/supported-models.html). A checkpoint loading in Transformers proves that Transformers understands it. It does not prove that TensorRT-LLM implements the same class or every requested feature. <!-- L47 --><!-- L48 --><!-- L49 -->

### Step 5: isolate the container boundary

Before importing TensorRT-LLM, prove that Docker passes the device through:

```bash
docker run --rm --gpus all nvidia/cuda:<pinned-runtime-tag> nvidia-smi
```

Use a real pinned tag selected from NVIDIA’s registry rather than copying the placeholder. The [NVIDIA Container Toolkit guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) documents Docker runtime configuration. If `nvidia-smi` works on the host but not in this container, rebuilding PyTorch cannot repair the container runtime. <!-- L61 --><!-- L62 -->

The downloadable `audit_stack.sh` collects these host, driver, compiler, tool, and environment facts without installing anything.

## Intuition: architecture targets are executable inventory

Think of a CUDA binary as a package containing several instruction manuals, each written for a class of GPU. The driver opens the package and selects a manual the assigned GPU understands. This analogy stops at dynamic behavior: a real runtime also resolves libraries, JIT-compiles PTX, loads kernels lazily, and can choose among algorithm implementations after inspecting shapes and dtypes.

The compiler works in two conceptual stages. CUDA source is first lowered for a virtual architecture such as `compute_75` or `compute_121`. It can then become machine code for a real architecture such as `sm_75` or `sm_121`. PTX preserves a virtual form for driver JIT. A fatbinary packages multiple outputs.

Figure 7 shows that pipeline.

![CUDA source compiling into virtual PTX and real cubins inside a fatbinary](FIG_07)
*Figure 7. A fatbinary can carry several native cubins and PTX. Each extra real target increases compilation work and artifact size; PTX adds a forward-JIT option rather than an optimized native image for every future GPU.*

The [NVCC manual](https://docs.nvidia.com/cuda/cuda-compiler-driver-nvcc/#gpu-compilation) allows `--generate-code` to be repeated:

```bash
nvcc kernel.cu \
  --generate-code arch=compute_75,code=sm_75 \
  --generate-code arch=compute_121,code=sm_121
```

That command is illustrative. It succeeds only when the selected compiler lists both targets and the source uses features valid for them. It also asks one artifact to span hardware generations with very different available features. Production libraries often compile selected kernels conditionally or stop carrying old targets rather than maintain every combination forever.

PTX is useful but easy to oversell. A baseline virtual target can JIT on later compatible hardware if the driver understands the embedded PTX version. It does not retroactively add source-level optimizations for the new architecture. Architecture-specific targets ending in `a`, introduced for newer capabilities, deliberately trade portability for features available only on that exact architecture. Family-specific targets ending in `f` sit between baseline and exact; the CUDA guide’s [feature-set target table](https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/compute-capabilities.html) documents which family targets cover which device capabilities. <!-- L17 -->

CMake gives these choices names. Figure 8 maps them to emitted code.

![CMake CUDA architecture values mapped to cubin and PTX outputs](FIG_08)
*Figure 8. `75-real` requests native `sm_75` code; `121-real` requests native `sm_121` code; a virtual target requests PTX. `native` asks CMake to infer from visible GPUs and is unsuitable for many cross-builds.*

Modern CMake uses the [`CUDA_ARCHITECTURES` target property](https://cmake.org/cmake/help/latest/prop_tgt/CUDA_ARCHITECTURES.html). The `-real` suffix selects cubin generation and `-virtual` selects PTX. The `native` value, available in CMake 3.24 and later, can be convenient on a developer workstation. It is fragile in a build farm where no GPU is visible or the build artifact must run elsewhere.

The lab’s minimal CUDA probe requires an explicit target:

```bash
cmake -S lab/cuda_probe -B build/cuda-probe -G Ninja \
  -DCUDA_TARGETS=75-real
cmake --build build/cuda-probe
./build/cuda-probe/cuda_arch_probe
```

For the newer device, change the value to `121-real` only after `nvcc --list-gpu-code` contains `sm_121`. The probe writes `__CUDA_ARCH__` from inside the launched kernel. That proves more than a successful configure: it proves that the built executable reached a code image on the device.

## Audit the compatibility stack from the bottom up

A reusable audit records evidence, not conclusions such as “CUDA looks fine.” Figure 9 is the evidence matrix to keep beside an incident report.

![Evidence matrix for host, driver, compiler, PyTorch, extension, model, and serving runtime](FIG_09)
*Figure 9. Each row has a different authoritative observation. Preserve all rows because later package changes can invalidate only one layer.*

| Layer | Question | Evidence | Stop when |
|---|---|---|---|
| Host | Can this executable format run here? | `uname -m`, Python platform, wheel tags, container architecture | CPU architecture or OS baseline is wrong |
| Device assignment | Is the intended GPU visible? | GPU UUID, name, compute capability, `CUDA_VISIBLE_DEVICES` | the process sees the wrong/no GPU |
| Driver | Can it initialize the device and load the chosen runtime family? | driver version and NVIDIA compatibility matrix | driver is below the runtime requirement |
| Toolkit/compiler | Can this `nvcc` generate the requested target? | resolved compiler path, version, `--list-gpu-arch`, `--list-gpu-code` | target is absent |
| PyTorch binary | Does core PyTorch contain compatible executable code? | version, `torch.version.cuda`, arch list, warning, synchronized operation | core operation fails |
| Extension | Was the out-of-tree library compiled for this device and ABI? | build log, binary inspection, extension smoke test | extension alone fails |
| Model integration | Does this release implement the resolved class and features? | immutable model revision and release model matrix | class/feature is absent |
| Runtime | Can the exact request fit and execute? | server log, precision, shapes, memory, request | kernel, shape, or memory error remains |

The order matters. A source build is wasted if Docker assigned no GPU. A TensorRT-LLM rebuild is wasted if core PyTorch cannot add two CUDA tensors. A model quantization experiment is irrelevant if the runtime has no implementation for the checkpoint class.

Treat environment resolution as part of the binary. Record:

```bash
which python
python -m pip --version
python -m pip freeze

which nvcc
readlink -f "$(which nvcc)"

printf '%s\n' "$CUDA_HOME" "$CUDAToolkit_ROOT" "$LD_LIBRARY_PATH"
```

For a container, add the image tag and immutable digest. For a source checkout, add `git rev-parse HEAD`, submodule revisions, compiler versions, CMake cache, and the final build log. A branch name such as `main` is never enough to reproduce a build.

One subtle boundary is worth making explicit: a wheel’s CUDA suffix describes the CUDA runtime family used to build or package it. It is not the device compute capability. `torch==...+cu130` does not mean `sm_130`, just as `sm_121` does not imply CUDA Toolkit 12.1.

## Turn failure time into artifact ownership

The first failure phase is evidence about ownership. Treat “CUDA error” as a family name, then preserve the earliest precise message before a framework catches it, retries, falls back, or wraps it in a server exception. A failure during CMake configuration, shared-library import, first synchronized tensor operation, model construction, and live request execution points at five different boundaries. Collapsing them into one ticket is how teams end up rebuilding the largest component without changing the artifact that failed.

Figure 10 maps each phase to the artifact that owns its repair.

![Five failure phases on a timeline, each with its error signature, owning artifact, and the wrong reflex](FIG_10)
*Figure 10. The phase that failed names the artifact to repair. The struck-through row is the reflex that costs a day: each one changes a component the failure never implicated.*

### Configure and compile failures

A compiler that rejects `sm_121` has not said anything about the installed PyTorch wheel. It has said that the `nvcc` selected for this build does not accept that target. Confirm the resolved compiler path, delete only the disposable probe build directory or use a new one, and configure the minimal CUDA probe with the same target. If the probe fails during compiler identification, stop below PyTorch. Select a Toolkit that knows the target and confirm its host-compiler requirements before returning to the package build.

CMake adds another source of ambiguity because architecture selection is cached. Changing `CUDA_HOME`, `CUDAToolkit_ROOT`, or `PATH` after the first configure does not guarantee that an existing build tree will forget its compiler. Compare the cache’s compiler path with `command -v nvcc`; if they differ, the build log is describing a different toolchain from the shell audit. The safe diagnostic pattern is a new, narrowly scoped build directory whose configure command records the compiler and architecture values explicitly.

`CMAKE_CUDA_ARCHITECTURES` initializes architecture targets for CUDA compilation; it does not patch an already-built wheel or change which images the driver finds inside a loaded shared object. `75-real` and `121-real` request native machine code when the compiler recognizes those values. A virtual target requests PTX. `native` asks CMake to infer from GPUs visible on the build host, which is useful for a local probe but dangerous for cross-builds, GPU-less CI workers, and artifacts intended for a heterogeneous fleet. <!-- L18 --><!-- L19 --><!-- L20 --><!-- L21 --><!-- L22 -->

### Import and dynamic-link failures

An import-time `undefined symbol` error is not evidence of a missing SM image. It usually means the extension and the libraries loaded into the process disagree at a symbol or ABI boundary. Record the extension path, inspect its dynamic dependencies with `ldd`, record the active Python and PyTorch versions, and compare PyTorch’s C++ ABI setting with the extension build. Rebuilding with another `TORCH_CUDA_ARCH_LIST` cannot repair an unresolved host symbol if the extension was compiled against a different PyTorch or C++ ABI. <!-- L29 -->

The reverse is also possible: an extension can import cleanly because its host registration code is valid, then fail only when its first CUDA kernel launches. Import proves that the CPU-side loader resolved enough symbols to initialize the module. It does not prove that every device function in the shared object has a compatible cubin or PTX image. That is why the sample extension test launches a kernel, synchronizes, and checks a result instead of ending after `import architecture_probe`.

Dependency order matters when PyTorch, ONNX Runtime, and another native package carry CUDA or cuDNN libraries. Record what the process actually loads; do not infer it from package names. ONNX Runtime documents CUDA and cuDNN major-family requirements and notes that importing PyTorch can preload compatible libraries in a shared environment. That can be convenient, but it also means import order may hide or expose a mixed-library environment. A clean environment with pinned packages is stronger evidence than a notebook kernel that has accumulated imports. <!-- L34 -->

### Kernel-launch and framework-core failures

When device enumeration succeeds but the first synchronized PyTorch operation fails, the boundary has moved above the driver and below the model. Reproduce with an operation owned by PyTorch core, not a fused attention package or application extension. Capture the PyTorch warning, device capability, `get_arch_list()` output, build CUDA version, and full exception together. The literal absence of `sm_121` remains insufficient: PyTorch’s own compatibility logic may accept a baseline or family image that covers the device. The synchronized operation decides whether the installed binary actually executes this path. <!-- L23 --><!-- L24 --><!-- L72 -->

If core PyTorch passes, establish a differential test: run the smallest failing extension call with the same process, device, dtype, and synchronization. A core pass plus extension fail gives you a narrow owner. Replace or rebuild that extension with `TORCH_CUDA_ARCH_LIST` first, then repeat the pre-repair and post-repair tests. Do not upgrade five packages simultaneously; doing so destroys the comparison that proved which artifact was missing coverage. <!-- L25 --><!-- L26 -->

If core PyTorch fails and no compatible published wheel satisfies the version constraint, the full source build becomes justified. The build must use a PyTorch revision whose source recognizes the device family and a Toolkit whose compiler lists the target. This is the conditional new-SM case: the expensive action follows a failed executable test and an exhausted replacement option, not a device-name heuristic. <!-- L66 --><!-- L71 -->

### Model-load and request-time failures

A model-construction failure belongs above CUDA code-image selection when core and extension probes pass. Separate an unknown model class from an unsupported feature combination. The first is an adapter or registry problem; the second may involve quantization, attention mode, parallelism, or precision. Compare the resolved immutable checkpoint configuration with the model and feature tables for the exact TensorRT-LLM release. Compiling the same native code again cannot create a missing Python adapter or implement an absent model feature. <!-- L47 --><!-- L48 --><!-- L49 --><!-- L67 -->

A server that starts but fails on a request has crossed still more gates. Preserve prompt length, requested output length, batch or concurrency state, precision, free memory, selected kernels, and fallback messages. An out-of-memory error at high concurrency does not invalidate a successful architecture probe. A shape assertion does not mean the cubin is wrong. A fallback warning followed by correct output is neither a native optimized-path result nor a failure; it is an observed fallback on that exact stack.

The resulting incident packet should be small but complete: immutable container digest or package lock, GPU UUID and compute capability, driver and compiler identities, PyTorch and runtime versions, first failing command, full earliest error, and the smallest passing command immediately below it. That pair—a passing lower boundary and failing next boundary—is more useful than a long build transcript because it assigns the repair to one artifact.

## Choose the smallest valid repair

The repair ladder in Figure 11 is the core operational policy of this guide.

![Repair ladder from replacing a wheel through extension, PyTorch, TensorRT-LLM, and runtime changes](FIG_11)
*Figure 11. Start with a compatible published artifact. Rebuild one extension before PyTorch, and PyTorch before TensorRT-LLM, unless the audit identifies a higher native component as the first failing layer.*

### Repair 0: replace the published wheel or container

If PyTorch reports that another wheel family for the same release covers the GPU, install that wheel in a new environment and repeat the core operation. If NVIDIA’s TensorRT-LLM release container already covers the complete supported stack, use it before assembling packages by hand. Replacement is a smaller, more reproducible repair than source compilation.

Never let `pip` silently replace the PyTorch build you selected. TensorRT-LLM 1.2’s [pip instructions](https://nvidia.github.io/TensorRT-LLM/1.2.0/installation/linux.html) warn that dependency resolution can swap an intended CUDA-compatible PyTorch package for another build. Capture `pip install --dry-run` where available, use an isolated environment, and constrain the exact torch build. <!-- L44 -->

### Repair 1: rebuild one CUDA extension

Choose this when the PyTorch core operation passes but an imported module such as a custom operator, attention package, or local extension fails with a missing kernel image. PyTorch’s [C++ extension documentation](https://docs.pytorch.org/docs/stable/cpp_extension.html) defines `TORCH_CUDA_ARCH_LIST` for this scope:

```bash
cd lab/extension_probe

TORCH_CUDA_ARCH_LIST="7.5" python -m pip install -v .  # T4 native target
python test_extension.py
```

On a compiler/source combination that recognizes the newer target:

```bash
TORCH_CUDA_ARCH_LIST="12.1" python -m pip install -v .
```

Use `12.1+PTX` only when you intentionally want the corresponding cubin plus the forward-JIT PTX behavior defined by PyTorch tooling. Adding more targets increases build time because the compiler emits more device images. Do not rebuild PyTorch just because `xformers`, FlashAttention, or your own `.so` was compiled without the local target. <!-- L25 --><!-- L26 -->

The extension must also match PyTorch’s C++ ABI. Query `torch.compiled_with_cxx11_abi()` and rebuild against the installed PyTorch headers and libraries. An architecture-correct `.so` can still fail at import with undefined symbols if it was compiled against a different ABI or PyTorch release.

### Repair 2: rebuild PyTorch itself

Choose this when all of the following are true:

1. The driver and selected Toolkit are valid for the device.
2. `nvcc` recognizes the desired target.
3. PyTorch’s warning and a synchronized core operation show that the installed PyTorch binary has no compatible code image.
4. No acceptable official wheel covers the device under your version constraints.
5. The pinned PyTorch source revision recognizes the target and builds with the selected Toolkit, cuDNN, and host compiler.

This is the conditional `sm_121` repair. The trigger is not “the GPU is new.” It is “PyTorch core is the first artifact that fails, and replacement cannot satisfy the version constraint.”

### Repair 3: rebuild TensorRT-LLM

Choose this only after PyTorch core and the model’s ordinary PyTorch path work, while a TensorRT-LLM native component is demonstrably the uncovered layer. TensorRT-LLM’s [1.2 source-build guide](https://nvidia.github.io/TensorRT-LLM/1.2.0/installation/build-from-source-linux.html) builds C++ components and a wheel. It accepts CMake-style architecture values:

```bash
python3 scripts/build_wheel.py --cuda_architectures "121-real"
```

That example is conditional. A source build cannot make 1.2 support a model adapter or GPU path absent from the release. The same guide estimates roughly 63 GB to construct the full Docker image, so this is not a diagnostic first move. <!-- L58 --><!-- L59 --><!-- L60 -->

### Repair 4: pin a different product version or runtime

If the compiler removed an old SM, the product removed its implementation, or the selected feature depends on hardware the GPU lacks, no architecture flag restores it. For T4, a known older TensorRT-LLM/PyTorch/CUDA combination may execute the needed model while 1.2 does not. Pin that complete tuple and accept its security and maintenance implications, or choose plain PyTorch, ONNX Runtime CUDA, or another maintained inference runtime that still covers the device. <!-- L65 -->

## Build PyTorch when the framework binary is the broken layer

A full PyTorch build is a software-supply-chain event. It produces hundreds of native components, binds to a Python ABI and C++ ABI, consumes a specific CUDA/cuDNN/compiler stack, and can take substantial compute and disk. Keep the existing working environment intact and build in a new one.

Figure 12 shows the controlled pipeline.

![Pinned PyTorch source flowing through Python build frontend, CMake, Ninja, NVCC, and verification](FIG_12)
*Figure 12. Pin the source and toolchain before compilation. The deliverable is not “build completed”; it is an installable artifact whose metadata and core CUDA operation pass on the target device.*

### 1. Pin source and dependencies

PyTorch’s official repository provides the current [source-build prerequisites and frontend](https://github.com/pytorch/pytorch#installation). Use the instructions from the tag or commit you will build, not a mixture of `main` documentation and an older release checkout. <!-- L27 --><!-- L28 -->

```bash
git clone --recursive https://github.com/pytorch/pytorch.git
cd pytorch
git checkout <audited-commit>
git submodule sync
git submodule update --init --recursive

python3 -m venv ../venv-pytorch-sm121
source ../venv-pytorch-sm121/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

Install the exact prerequisites documented by that revision. Current PyTorch source requires a modern C++ compiler and uses CMake under its Python build frontend. CUDA builds additionally need a supported Toolkit and cuDNN. “Supported” here is a relation among the PyTorch revision, CUDA release, host compiler, and host architecture; it is not inferred from any one version number.

### 2. Prove the target exists at source and compiler layers

```bash
export CUDA_HOME=/usr/local/cuda-<selected-version>
export PATH="$CUDA_HOME/bin:$PATH"

nvcc --version
nvcc --list-gpu-arch | grep '^compute_121$'
nvcc --list-gpu-code | grep '^sm_121$'

grep -n "'12.1'" torch/utils/cpp_extension.py
git rev-parse HEAD
```

The first pair proves compiler recognition. The source search is a useful early rejection test, not a full support proof. Current PyTorch `cpp_extension.py` lists 12.1 among known extension targets, but the exact set changes; that is why the checkout must be pinned.

If native `sm_120` code is already compatible with the 12.1 device and passes real operations, stop. Rebuilding solely to make `sm_121` appear in a list violates the smallest-repair rule. Build an exact target only when you have a demonstrated functional gap or a measured, controlled reason to replace compatible generic or family code with a native artifact.

### 3. Configure the supported frontend

PyTorch’s top-level build is not a standalone tutorial CMake project. Its Python frontend prepares generated sources and forwards supported variables into CMake. For the pinned build:

```bash
export TORCH_CUDA_ARCH_LIST="12.1"
export CMAKE_PREFIX_PATH="${VIRTUAL_ENV}:${CMAKE_PREFIX_PATH:-}"
export MAX_JOBS=4

python -m pip install --no-build-isolation -v -e . 2>&1 \
  | tee ../pytorch-sm121-build.log
```

The current PyTorch README documents the editable `pip` command. `MAX_JOBS` limits parallel compilation pressure; choose it from available CPU and memory rather than copying four as a performance optimum. The build log must show the intended CUDA compiler and generated target flags.

If you need a distributable wheel rather than an editable installation, use the packaging command documented or exercised by the pinned revision’s CI. Current source supports a `bdist_wheel` path, exposed by the companion driver as `BUILD_MODE=wheel`, but packaging contracts can change:

```bash
PYTORCH_SOURCE="$PWD" TARGET_CC=12.1 BUILD_MODE=wheel \
  ../lab/build_pytorch_for_arch.sh
```

Do not name the wheel as though it were an official PyTorch binary. Store the source commit, submodules, compiler versions, build flags, Python tag, host architecture, and checksum beside it.

### 4. Verify the installed result, not the build process

Open a clean shell or environment so an old `torch` import cannot shadow the new one:

```bash
python - <<'PY'
import torch

print(torch.__version__)
print(torch.version.cuda)
print(torch.cuda.get_arch_list())
print(torch.compiled_with_cxx11_abi())
print(torch.cuda.get_device_name(0))
print(torch.cuda.get_device_capability(0))

x = torch.randn(1024, 1024, device="cuda")
y = x @ x.T
torch.cuda.synchronize()
print(y.shape, y.dtype, y.device)
PY
```

Then rebuild every C++/CUDA extension against this PyTorch build. A passing matrix multiplication proves several core paths, but not every dtype, sparse operator, distributed collective, attention kernel, or model feature. Run the application’s operator-level and model-level tests before calling the build usable.

## Check transformer and model support separately

Once tensors execute, the next failure domain is the model. Figure 13 connects transformer shapes to the state an inference server manages.

![Transformer Q K V tensor shapes and KV-cache growth during autoregressive decoding](FIG_13)
*Figure 13. Prefill computes attention across the prompt. Decode reuses cached keys and values and appends state for each generated token, so memory grows with layers, active sequences, and retained tokens.*

The original [Transformer paper](https://arxiv.org/abs/1706.03762) defines scaled dot-product attention. Modern LLMs vary the number of query and key/value heads, normalization, positional encoding, feed-forward blocks, sparsity, and routing. Runtime support therefore attaches to a model architecture and feature combination, not to the word “transformer.” <!-- L01 --><!-- L02 -->

TensorRT-LLM 1.2 publishes a [PyTorch-backend model table and feature matrix](https://nvidia.github.io/TensorRT-LLM/1.2.0/models/supported-models.html). Check four gates in order:

1. **Class:** does the resolved Hugging Face architecture map to an implemented TensorRT-LLM model?
2. **Feature combination:** does that model support the requested CUDA Graph, overlap scheduler, chunked prefill, guided decoding, speculative decoding, LoRA, or cache behavior?
3. **Precision and kernel path:** can this GPU and release execute the selected weight, activation, and cache dtypes?
4. **Memory and shapes:** do weights, KV cache, activations, workspaces, and runtime overhead fit for the real request distribution?

Figure 14 makes those gates independent.

![Four separate model gates for CUDA execution, adapter, feature and precision, and memory](FIG_14)
*Figure 14. Recompiling for the SM opens only the CUDA-execution gate. It cannot create a missing model adapter, feature implementation, numerical validation, or memory capacity.*

Optimized attention illustrates why a fallback may exist on one GPU and not another. [FlashAttention](https://papers.nips.cc/paper_files/paper/2022/hash/67d57c32e20fd0a7a302cb81d36e40d5-Abstract-Conference.html) reorganizes exact attention around tiling and memory traffic. An implementation chooses tile sizes and instructions around GPU resources. If one fused kernel rejects a head dimension or SM, the runtime may select an unfused implementation, as the historical T4 trace did. That fallback can be slower, consume more memory, or be absent for another dtype or shape. Only the exact workload reveals the result. <!-- L03 -->

Serving adds a state-management problem. [PagedAttention](https://doi.org/10.1145/3600006.3613165) introduced block-based KV-cache management in vLLM; TensorRT-LLM has its own executor and KV-cache manager. Its [architecture overview](https://nvidia.github.io/TensorRT-LLM/1.2.0/developer-guide/overview.html) separates request scheduling, KV-cache allocation, model execution, and sampling. CUDA Graphs can amortize repeated launch setup on compatible execution paths, while an overlap scheduler can perform some CPU work for one step as the GPU starts another. None of those mechanisms changes whether the base model fits. <!-- L04 --><!-- L50 --><!-- L51 --><!-- L52 --><!-- L53 --><!-- L54 -->

## Choose the deployment branch: TensorRT-LLM or ONNX

TensorRT-LLM and ONNX solve different integration problems. Figure 15 is the fork to keep in mind.

![Hugging Face checkpoint branching to modern TensorRT-LLM or ONNX then TensorRT and ONNX Runtime](FIG_15)
*Figure 15. TensorRT-LLM 1.2 loads supported Hugging Face checkpoints through its PyTorch backend. ONNX is an interchange branch consumed by generic TensorRT or ONNX Runtime.*

### Branch A: supported generative model through TensorRT-LLM

In TensorRT-LLM 1.2, NVIDIA removed the legacy TensorRT engine backend. The [migration guide](https://nvidia.github.io/TensorRT-LLM/latest/legacy/tensorrt-backend-removal.html) says PyTorch is the sole execution backend, `LLM(backend="tensorrt")` is removed, and Hugging Face checkpoints load directly. Old tutorials centered on `convert_checkpoint.py`, `trtllm-build`, serialized TensorRT-LLM engines, or `backend="tensorrt"` are not the 1.2 happy path. <!-- L40 --><!-- L41 --><!-- L42 -->

Use this branch when the release model table contains the architecture, the feature and precision combination is viable, and you want TensorRT-LLM’s LLM-specific executor, scheduling, KV-cache management, sampling, and OpenAI-compatible serving.

### Branch B: PyTorch to ONNX to TensorRT or ONNX Runtime

[ONNX](https://onnx.ai/onnx/repo-docs/IR.html) is a versioned computation-graph format. A model declares the operator sets it imports. The declaration defines operator contracts; it does not promise that a consumer has a fused or fast kernel for every node. <!-- L30 --><!-- L31 --><!-- L64 -->

Use this branch when the target runtime accepts ONNX and the graph can be exported under its operator and shape constraints. PyTorch’s current [ONNX exporter](https://docs.pytorch.org/docs/stable/onnx_export.html) uses a `torch.export`-based path with `dynamo=True`; `dynamic_shapes` is preferred for that path. Then: <!-- L32 --><!-- L33 --><!-- L36 --><!-- L37 -->

- run the ONNX checker;
- run shape inference, understanding that data-dependent shapes can remain unresolved;
- test numerics against PyTorch on representative inputs;
- parse and build with the exact TensorRT release, or create an ONNX Runtime session;
- define TensorRT optimization profiles for dynamic dimensions.

ONNX Runtime’s [TensorRT Execution Provider guide](https://onnxruntime.ai/docs/execution-providers/TensorRT-ExecutionProvider.html) recommends registering the TensorRT provider before CUDA so unsupported subgraphs can fall back to CUDA. That is fallback between execution providers. It is not evidence that every unsupported TensorRT node will be fast or that CPU fallback never occurs. Inspect the actual session providers and profiling output. <!-- L35 -->

Generic TensorRT serializes GPU-specific engines by default. NVIDIA’s [version-compatibility documentation](https://docs.nvidia.com/deeplearning/tensorrt/10.x.x/inference-library/version-compatibility.html) describes compatibility modes and their trade-offs. Move ONNX graphs between build hosts if useful; do not casually copy one engine plan from T4 to `sm_121` and expect it to deserialize. <!-- L38 --><!-- L39 -->

## Install and run TensorRT-LLM 1.2 honestly

Use the versioned release container for the first experiment. It collapses Python, PyTorch, CUDA user-space libraries, TensorRT-LLM, and auxiliary dependencies into one signed artifact while leaving the host driver outside. <!-- L45 -->

```bash
docker run --rm -it \
  --ipc host \
  --gpus all \
  --ulimit memlock=-1 \
  --ulimit stack=67108864 \
  -p 8000:8000 \
  nvcr.io/nvidia/tensorrt-llm/release:1.2.0
```

This is the command in NVIDIA’s [1.2 quick-start guide](https://nvidia.github.io/TensorRT-LLM/1.2.0/quick-start-guide.html). In a controlled environment, resolve and record the image digest after pulling. Inside the container, capture the stack before loading a model:

```bash
python - <<'PY'
import torch
import tensorrt_llm

print("TensorRT-LLM", tensorrt_llm.__version__)
print("PyTorch", torch.__version__)
print("PyTorch CUDA", torch.version.cuda)
print("architectures", torch.cuda.get_arch_list())
print("device", torch.cuda.get_device_name(0))
print("capability", torch.cuda.get_device_capability(0))
PY
```

For a GPU named on the official 1.2 hardware page, this begins a documented configuration check. For T4, it is an experiment on unlisted hardware. A successful import proves only import. Run a core PyTorch operation, the selected model, and the intended precision.

Direct generation uses the modern `LLM` API:

```bash
python lab/run_trtllm.py \
  --model TinyLlama/TinyLlama-1.1B-Chat-v1.0 \
  --max-tokens 64
```

NVIDIA uses the same model in its 1.2 installation sanity check. Pin the Hugging Face revision for a reproducible deployment instead of accepting a moving repository default.

To serve it:

```bash
trtllm-serve "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
```

`trtllm-serve` exposes an OpenAI-compatible HTTP service. Do not add `trtllm-build` before this command for the 1.2 PyTorch path. <!-- L55 -->

Figure 16 is how to report the T4 outcome.

![Matrix separating official validation, observed execution, optimized kernels, and fallbacks](FIG_16)
*Figure 16. “Not listed,” “failed,” “ran with fallback,” and “ran an optimized path” are four different observations. Record the exact stack and do not promote one cell into another.*

Use these result labels:

- **1.2 validated hardware:** only when the release page names the applicable product or configuration.
- **Observed working:** exact container digest, model revision, precision, shapes, and request completed.
- **Observed fallback:** the logs identify a fallback and the request completed; report the warning and performance separately.
- **Observed failure:** preserve the first relevant error and the audit tuple. Do not rewrite it as “T4 cannot run inference.”

The bare-metal pip path has more degrees of freedom. TensorRT-LLM 1.2’s install page documents Ubuntu 24.04, a CUDA 13.1 Toolkit, and PyTorch 2.9.1 from the CUDA 13.0 wheel index for its prebuilt wheel path. Those pins belong together. If your custom PyTorch build differs, assume native-extension and ABI compatibility must be proven; do not mix packages until `pip` happens to resolve. <!-- L43 -->

## The math: attention shapes and KV-cache capacity

Architecture compatibility answers whether kernels can launch. Tensor shapes answer whether the model is correct and whether the workload fits. Define the quantities before calculating memory:

| Symbol | Meaning | Units |
|---|---|---|
| $B$ | batch size during one model step | sequences |
| $L$ | number of transformer layers | layers |
| $T_q$ | query length for the current attention operation | tokens |
| $T_{kv}$ | retained key/value length | tokens |
| $H_q$ | number of query heads | heads |
| $H_{kv}$ | number of key/value heads | heads |
| $D$ | dimension of one attention head | elements/head |
| $S$ | simultaneously active sequences whose cache is resident | sequences |
| $b$ | storage per cached scalar | bytes/element |
| $P$ | model parameter count | parameters |

For one layer, write queries as $`Q \in \mathbb{R}^{B \times H_q \times T_q \times D}`$. Keys and values have shapes $`K,V \in \mathbb{R}^{B \times H_{kv} \times T_{kv} \times D}`$. In ordinary multi-head attention, $H_q=H_{kv}$. In grouped-query attention, several query heads share each key/value head, so $H_{kv}<H_q$.

The attention operation is:

$$
A = \operatorname{softmax}\!\left(\frac{QK^\top}{\sqrt{D}} + M\right),
\qquad O = AV
$$

$M$ is the causal or padding mask, $A$ contains attention weights, and $O$ is the head output. During prompt prefill, both token axes can be long. During autoregressive decode, $T_q$ is usually one for each active sequence while $T_{kv}$ grows as tokens are retained.

A naive implementation materializes an attention-score tensor proportional to $`B H_q T_q T_{kv}`$. FlashAttention remains mathematically exact but tiles the calculation so it does not need to move that full intermediate repeatedly through high-bandwidth memory. This is an algorithmic memory-traffic improvement; it does not make the persistent KV cache disappear.

Ignoring allocator fragmentation, metadata, alignment, cache block rounding, and optional extra state, the resident KV values require approximately:

$$
M_{KV} \approx 2L T_{kv} H_{kv} D b S
$$

The leading 2 stores both keys and values. Memory grows linearly with retained tokens, layers, KV heads, head dimension, bytes per element, and active sequences. This is why a model that generates successfully at concurrency one can fail when a server admits more requests.

Use a concrete hypothetical configuration: 32 layers, 8 KV heads, head dimension 128, 4,096 retained tokens, 16 active sequences, and two bytes per cached value. Then:

$$
\begin{aligned}
M_{KV}
&\approx 2 \times 32 \times 4096 \times 8 \times 128 \times 2 \times 16 \\
&= 8{,}589{,}934{,}592\ \text{bytes} \\
&= 8\ \text{GiB}
\end{aligned}
$$

That workload needs about 8 GiB for raw KV values alone. It still needs model weights, activations, CUDA and communication workspaces, graph-capture pools, allocator headroom, and the server process.

Only $S$ moves when a server admits more traffic. Figure 17 holds the same configuration and varies nothing but the number of resident sequences.

![KV cache bars for one, four, and sixteen sequences against the headroom left by the fixed terms](FIG_17)
*Figure 17. At the configuration above the cache costs 0.5 GiB per resident sequence. The weights, activations, and workspaces do not grow with $S$, so concurrency alone decides whether the same model and the same kernels still fit.*

A first weight estimate is:

$$
M_{weights} \approx P b_w
$$

$b_w$ is the average stored bytes per parameter. This estimate helps reject an impossible plan, but it is not an allocation prediction. Quantized formats can add scales, zero points, padding, or duplicated packed representations, and some runtimes retain higher-precision tensors for selected operations.

A conservative capacity test is therefore:

$$
M_{weights} + M_{KV} + M_{activations} + M_{workspaces} + M_{runtime}
< M_{usable\ GPU}
$$

The right side is deliberately “usable GPU memory,” not the product’s advertised capacity. Measure it after the process and framework initialize, leave operating headroom, and validate at the longest admitted prompt and output lengths. TensorRT-LLM’s KV-cache memory fraction is a policy knob within this budget, not extra physical memory.

Grouped-query attention makes the role of $H_{kv}$ visible. Holding the other quantities constant, moving from 32 KV heads to 8 divides the raw KV estimate by four. Lower-precision KV storage reduces $b$, but only when the GPU, model implementation, accuracy target, and runtime support that cache format. Do not infer an available precision from a data-type name in generic TensorRT documentation; check the model and feature matrix for the pinned TensorRT-LLM release. <!-- L63 -->

## Implementation: a reproducible sequence

The companion files are deliberately small. They make each compatibility boundary observable before the next expensive step.

### 1. Capture the host audit

```bash
bash lab/audit_stack.sh | tee host-audit.txt
python lab/audit_torch.py | tee torch-audit.json
```

Run this once on the host and again inside the intended container. A difference in visible GPU UUID, CPU architecture, `nvcc`, PyTorch version, or compiled architecture list is not noise. It identifies the boundary that changed.

### 2. Compile the smallest independent CUDA program

For T4:

```bash
cmake -S lab/cuda_probe -B build/t4-probe -G Ninja \
  -DCUDA_TARGETS=75-real
cmake --build build/t4-probe
./build/t4-probe/cuda_arch_probe
```

For native `sm_121`, only after the compiler lists the target:

```bash
cmake -S lab/cuda_probe -B build/sm121-probe -G Ninja \
  -DCUDA_TARGETS=121-real
cmake --build build/sm121-probe
./build/sm121-probe/cuda_arch_probe
```

This isolates the driver, Toolkit, CMake, and target from PyTorch. If it fails during compiler identification, do not edit PyTorch. If it builds but fails at kernel launch, preserve the exact CUDA error and inspect the emitted artifact with the CUDA binary tools shipped by your selected Toolkit.

### 3. Prove extension-only repair first

```bash
cd lab/extension_probe
TORCH_CUDA_ARCH_LIST="7.5" python -m pip install -v .
python test_extension.py
```

Repeat with `12.1` only in the audited new-device environment. The test synchronizes after launching the extension kernel. A successful package build without the test is not a result.

If core PyTorch passes and this extension fails before rebuilding, then passes after rebuilding, stop. You fixed the smallest broken artifact. Recompiling PyTorch or TensorRT-LLM would only enlarge the change surface.

### 4. Gate the full PyTorch build

The downloadable `build_pytorch_for_arch.sh` driver refuses to start when `nvcc` does not list the virtual target or when the pinned source does not list the requested architecture in its extension tooling. It still does not install system prerequisites or decide which PyTorch commit supports your CUDA release; those choices must come from the pinned upstream documentation.

```bash
export PYTORCH_SOURCE=/absolute/path/to/pinned/pytorch
export TARGET_CC=12.1
export MAX_BUILD_JOBS=4
export BUILD_MODE=editable

bash lab/build_pytorch_for_arch.sh
python lab/audit_torch.py
```

The `editable` mode follows the current official source-build frontend. Select `wheel` only after checking the pinned revision’s packaging path. In either case, a custom artifact must carry provenance and must be verified in a fresh environment.

### 5. Run the direct TensorRT-LLM branch

Inside the 1.2 release container:

```bash
python lab/run_trtllm.py --max-tokens 64

trtllm-serve "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
```

For reproducibility, first materialize an immutable Hugging Face snapshot into a local directory and pass that directory to the program and server. Keep authentication tokens out of shell history and build logs. Capture server startup logs because they reveal selected kernels, fallbacks, memory allocation, and model configuration.

### 6. Run the separate ONNX branch

The included exporter uses a small embedding-plus-projection graph. It tests the exporter, dynamic shape declaration, ONNX checker, shape inference, and execution-provider selection without pretending that every LLM exports cleanly.

```bash
python -m pip install torch onnx onnxscript onnxruntime-gpu

python lab/export_onnx.py --output token-projector.onnx
python lab/run_onnx.py token-projector.onnx \
  --batch 2 --sequence 16
```

The runner requests providers in the order TensorRT, CUDA, then CPU, but only if they are installed. It prints the providers actually attached to the session. A session listing `TensorrtExecutionProvider` does not prove that every node ran in TensorRT; enable runtime profiling and inspect graph partitioning before making that claim.

For a real transformer, compare PyTorch and ONNX outputs using fixed inputs and tolerances chosen for the precision. Exercise minimum, optimum, and maximum shapes intended for TensorRT profiles. Export success does not validate autoregressive cache semantics, tokenizer behavior, sampling, or numerical quality.

### 7. Benchmark the server without inventing a result

Figure 18 places the online-serving metrics on one request timeline.

![Request timeline showing time to first token, inter-token latency, end-to-end latency, and throughput](FIG_18)
*Figure 18. Time to first token (TTFT) ends at the first streamed token; inter-token latency describes the gaps that follow; end-to-end latency ends at completion. Throughput aggregates work across requests and cannot replace the latency distribution.*

NVIDIA’s TensorRT-LLM 1.2 benchmarking documentation distinguishes throughput and latency and exposes workload controls such as input/output lengths, request rate or concurrency, warm-up, parallelism, streaming, and KV-cache allocation. The companion script follows NVIDIA’s documented `aiperf` serving example and writes JSON instead of a made-up table: <!-- L56 --><!-- L57 -->

```bash
RESULT_DIR=benchmark-results/t4-run-001 \
REQUEST_COUNT=100 \
REQUEST_RATE=10 \
INPUT_TOKENS=128 \
OUTPUT_TOKENS=128 \
bash lab/benchmark.sh
```

Those values define a workload; they are not recommended capacity settings. A T4 may require a lower request rate or shorter lengths to complete. Changing them creates a different benchmark.

Copy the measured statistics into the downloadable `benchmark-report.md` template. At minimum record:

- GPU name, count, UUIDs, compute capability, and memory;
- driver, Toolkit, container digest, PyTorch, and TensorRT-LLM versions;
- model repository and immutable revision;
- weight, activation, and KV-cache precision;
- input and requested-output distributions, request count, rate, concurrency, and streaming mode;
- warm-up, parallelism, scheduler, and KV-cache settings;
- TTFT, time per output token or inter-token latency, end-to-end latency, token throughput, failures, and peak memory.

Do not compare a 128-token prompt at concurrency one with a long-tailed production trace at concurrency 32 and attribute the difference to GPU architecture. First hold the model revision, software stack, precision, and request distribution constant. Then change one factor.

## Limitations and common mistakes

This workflow narrows architecture failures. It cannot turn every model and GPU into a supported, accurate, or fast deployment.

> [!WARNING]
> **Common mistake: treating `nvidia-smi` as a Toolkit audit.** The command can show a high CUDA compatibility ceiling while `nvcc` is missing or points at another Toolkit. The symptom is a build that rejects the SM even though the driver looks new enough.

> [!WARNING]
> **Common mistake: exact-string testing for `sm_121`.** A compatible 12.x code image may run on the device. The symptom is an unnecessary multi-hour PyTorch rebuild even though a synchronized core operation already passes.

> [!WARNING]
> **Common mistake: rebuilding PyTorch for an extension failure.** When core matrix multiplication works and one imported `.so` fails, the extension owns the missing image. The symptom is a large custom PyTorch build followed by the same extension error because that `.so` was never rebuilt.

> [!WARNING]
> **Common mistake: setting a CMake target the compiler does not know.** `CMAKE_CUDA_ARCHITECTURES=121` is a request, not a compiler upgrade. The symptom is failure during compiler checks or `nvcc fatal: Unsupported gpu architecture`.

> [!WARNING]
> **Common mistake: assuming a successful build establishes product support.** A locally compiled TensorRT-LLM library can still lack the model adapter, feature combination, or maintained T4 kernel path. The symptom moves from compilation to import, model loading, kernel selection, or runtime execution.

> [!WARNING]
> **Common mistake: calling unlisted hardware impossible.** The T4 may execute a compatible path or a pinned older stack, and the project owner reports such field experience. The accurate statement is that TensorRT-LLM 1.2’s current hardware page does not validate T4. Test and report the exact tuple.

> [!WARNING]
> **Common mistake: inserting ONNX into the TensorRT-LLM 1.2 path.** The legacy TensorRT engine backend and `trtllm-build` workflow were removed. The symptom is following stale commands that do not exist or solve a different deployment problem.

> [!WARNING]
> **Common mistake: treating ONNX export as runtime validation.** A graph can serialize while TensorRT rejects an operator, dynamic profile, or dtype. ONNX Runtime can also partition the graph across providers. The symptom is fallback, build failure, or numerics that differ at shapes not tested during export.

> [!WARNING]
> **Common mistake: benchmarking only tokens per second.** Throughput can rise while TTFT or tail latency becomes unacceptable. The symptom is an impressive aggregate number attached to a poor interactive service.

PTX has limits. The driver must understand its version, and code using architecture-specific `a` features is not forward-portable to a different compute capability. A JIT path can also introduce first-run compilation behavior. Warm up deliberately and distinguish JIT or model-load time from steady request latency.

TensorRT engines have their own portability rules. An ONNX file is a graph interchange artifact; a serialized TensorRT plan is usually tied to the builder/runtime and GPU compatibility choices. Rebuild the engine or use documented compatibility modes rather than assuming a plan compiled on one GPU is universal.

Memory estimates are lower bounds. Allocator fragmentation, block rounding, graph pools, workspaces, communication buffers, and implementation-specific copies can invalidate a paper calculation. Validate admission limits under the real distribution and preserve OOM/fallback logs.

Finally, successful text generation is not an accuracy evaluation. A custom compiler, new kernel path, quantization mode, or ONNX conversion can change numerics. Compare logits or task metrics under an explicit tolerance and dataset before shipping.

## Key takeaways

- Compute capability identifies GPU features; CUDA Toolkit versions identify software releases. Audit both, plus the driver and host architecture.
- Compare PyTorch’s device capability and compiled code inventory, but let its compatibility warning and a synchronized core operation decide whether the wheel truly lacks executable code.
- Rebuild the lowest broken layer: one extension first, PyTorch only when core kernels are uncovered, and TensorRT-LLM only when its native component is the failing artifact.
- TensorRT-LLM 1.2 uses the PyTorch backend and loads supported Hugging Face checkpoints directly. ONNX is a separate route into TensorRT or ONNX Runtime.
- A T4 run can work without appearing on TensorRT-LLM 1.2’s validation page. Report it as observed execution on an exact stack, not as a universal vendor-support claim.
- Benchmark TTFT, token latency, end-to-end latency, throughput, failures, and memory with the full hardware, model, precision, and workload tuple.

## Try it yourself

1. Run `audit_stack.sh` and `audit_torch.py` on a GPU host. Explain which output describes hardware, which describes the driver, which describes the compiler, and which describes the installed PyTorch binary.
2. Build the CMake probe for one native architecture. Add a virtual target and inspect how the generated artifact changes with the binary inspection tools in the same Toolkit.
3. Build the sample PyTorch extension for the visible GPU. Then deliberately build it for a target that excludes that GPU in an isolated environment and capture the runtime error. Restore the correct build.
4. Resolve a model’s configuration at an immutable Hugging Face revision. Compare its declared architecture and requested features with the TensorRT-LLM 1.2 model matrix before downloading weights.
5. Start the 1.2 release container, run direct generation, then serve the same local model snapshot. On T4, classify the result using Figure 16 rather than the binary words “supported” or “unsupported.”
6. Run the ONNX toy graph at two shapes and print the attached execution providers. Inspect profiling before claiming TensorRT executed the entire graph.
7. Run the benchmark harness twice with one controlled change. Fill both reproducibility tuples before interpreting the delta.

## References

All web sources below were accessed on September 14–15, 2026. Only reader-facing sources are listed here; the private claim ledger is not a publication artifact.

### Lab downloads

- [`README.md`](LAB_01) — explains the lab layout, prerequisites, and recommended run order.
- [`audit_stack.sh`](LAB_02) — records host, driver, compiler, and environment evidence without installing anything.
- [`audit_torch.py`](LAB_03) — records PyTorch build metadata, device capability, warnings, and a synchronized CUDA probe.
- [`benchmark-report.md`](LAB_04) — template for recording a reproducible inference benchmark.
- [`benchmark.sh`](LAB_05) — runs the documented `aiperf` workload and exports its profile.
- [`build_pytorch_for_arch.sh`](LAB_06) — gates and starts a pinned architecture-aware PyTorch build.
- [`cuda_probe/CMakeLists.txt`](LAB_07) — configures the independent CUDA architecture probe.
- [`cuda_probe/probe.cu`](LAB_08) — launches a kernel and prints the device and compiled architecture selected at runtime.
- [`export_onnx.py`](LAB_09) — exports and validates the dynamic-shape ONNX probe graph.
- [`extension_probe/binding.cpp`](LAB_10) — exposes the sample CUDA extension to Python.
- [`extension_probe/kernel.cu`](LAB_11) — implements the synchronized sample extension kernel.
- [`extension_probe/setup.py`](LAB_12) — builds the sample extension with PyTorch tooling.
- [`extension_probe/test_extension.py`](LAB_13) — executes and validates the built extension.
- [`inspect_model.py`](LAB_14) — resolves model configuration and immutable revision without loading weights.
- [`run_onnx.py`](LAB_15) — runs the ONNX graph and reports the execution providers actually attached.
- [`run_trtllm.py`](LAB_16) — performs minimal TensorRT-LLM generation through the modern `LLM` API.

### CUDA and build systems

1. NVIDIA. [CUDA Programming Guide: The CUDA Platform](https://docs.nvidia.com/cuda/cuda-programming-guide/01-introduction/cuda-platform.html).
2. NVIDIA. [CUDA Programming Guide: Compute Capabilities](https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/compute-capabilities.html).
3. NVIDIA. [CUDA GPU Compute Capability Table](https://developer.nvidia.com/cuda/gpus).
4. NVIDIA. [CUDA Compiler Driver NVCC: GPU Compilation](https://docs.nvidia.com/cuda/cuda-compiler-driver-nvcc/#gpu-compilation).
5. NVIDIA. [CUDA Compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/latest/).
6. NVIDIA. [CUDA Toolkit, Driver, and Architecture Matrix](https://docs.nvidia.com/datacenter/tesla/drivers/cuda-toolkit-driver-and-architecture-matrix.html).
7. CMake. [`CMAKE_CUDA_ARCHITECTURES`](https://cmake.org/cmake/help/latest/variable/CMAKE_CUDA_ARCHITECTURES.html) and [`CUDA_ARCHITECTURES`](https://cmake.org/cmake/help/latest/prop_tgt/CUDA_ARCHITECTURES.html).

### PyTorch, ONNX, and TensorRT

8. PyTorch. [Official source repository and build instructions](https://github.com/pytorch/pytorch).
9. PyTorch. [C++ and CUDA extensions](https://docs.pytorch.org/docs/stable/cpp_extension.html).
10. PyTorch. [`torch.cuda` binary compatibility checks](https://github.com/pytorch/pytorch/blob/main/torch/cuda/__init__.py).
11. PyTorch. [ONNX exporter](https://docs.pytorch.org/docs/stable/onnx_export.html).
12. ONNX. [Intermediate Representation specification](https://onnx.ai/onnx/repo-docs/IR.html).
13. ONNX. [Shape inference API](https://onnx.ai/onnx/api/shape_inference.html).
14. ONNX Runtime. [CUDA Execution Provider](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html) and [TensorRT Execution Provider](https://onnxruntime.ai/docs/execution-providers/TensorRT-ExecutionProvider.html).
15. NVIDIA. [TensorRT capabilities](https://docs.nvidia.com/deeplearning/tensorrt/latest/inference-library/capabilities.html), [dynamic shapes](https://docs.nvidia.com/deeplearning/tensorrt/latest/inference-library/dynamic-shapes-basics.html), and [version compatibility](https://docs.nvidia.com/deeplearning/tensorrt/10.x.x/inference-library/version-compatibility.html).

### TensorRT-LLM 1.2

16. NVIDIA. [TensorRT-LLM 1.2 installation on Linux](https://nvidia.github.io/TensorRT-LLM/1.2.0/installation/linux.html).
17. NVIDIA. [TensorRT-LLM 1.2 source build](https://nvidia.github.io/TensorRT-LLM/1.2.0/installation/build-from-source-linux.html).
18. NVIDIA. [TensorRT-LLM 1.2 supported hardware](https://nvidia.github.io/TensorRT-LLM/1.2.0/supported-hardware.html).
19. NVIDIA. [TensorRT-LLM 1.2 supported models](https://nvidia.github.io/TensorRT-LLM/1.2.0/models/supported-models.html).
20. NVIDIA. [TensorRT-LLM architecture overview](https://nvidia.github.io/TensorRT-LLM/1.2.0/developer-guide/overview.html).
21. NVIDIA. [Migration guide: TensorRT backend removed](https://nvidia.github.io/TensorRT-LLM/latest/legacy/tensorrt-backend-removal.html).
22. NVIDIA. [`trtllm-bench`](https://nvidia.github.io/TensorRT-LLM/1.2.0/commands/trtllm-bench.html) and [`trtllm-serve` benchmarking](https://nvidia.github.io/TensorRT-LLM/1.2.0/commands/trtllm-serve/run-benchmark-with-trtllm-serve.html).
23. NVIDIA. [T4/`sm_75` fallback trace, TensorRT-LLM issue #1865](https://github.com/NVIDIA/TensorRT-LLM/issues/1865). Historical issue evidence, not an official 1.2 support statement.

### Transformer foundations

24. Vaswani et al. [Attention Is All You Need](https://arxiv.org/abs/1706.03762), 2017.
25. Dao et al. [FlashAttention](https://papers.nips.cc/paper_files/paper/2022/hash/67d57c32e20fd0a7a302cb81d36e40d5-Abstract-Conference.html), 2022.
26. Kwon et al. [Efficient Memory Management for Large Language Model Serving with PagedAttention](https://doi.org/10.1145/3600006.3613165), 2023.
