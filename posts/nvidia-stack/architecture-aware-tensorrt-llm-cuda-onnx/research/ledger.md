# Source ledger — architecture-aware-tensorrt-llm-cuda-onnx

## Brief

- **Working title:** From PyTorch Tensors to TensorRT-LLM: An Architecture-Aware CUDA and ONNX Inference Guide
- **Subject:** machine-learning systems and GPU software architecture
- **Depth:** L4 pillar (7,500–10,000 words; 12–18 figures)
- **Audience:** senior ML engineers, inference engineers, CUDA-aware platform engineers, and advanced students
- **Reader outcome:** audit a Linux host, distinguish a T4 (`sm_75`) product-validation gap from a new-device binary gap such as `sm_121`, rebuild only the smallest necessary CUDA layer (one extension, PyTorch, or TensorRT-LLM), choose correctly between modern TensorRT-LLM and ONNX/TensorRT, then run and benchmark real inference
- **Version baseline:** TensorRT-LLM 1.2.0, the latest stable release found during research on 2026-09-14; release-candidate material is excluded from the executable path

## Sources

| ID | Tier | Source | URL | Accessed |
|---|---|---|---|---|
| S01 | T1 | Vaswani et al., “Attention Is All You Need,” arXiv:1706.03762 | https://arxiv.org/abs/1706.03762 | 2026-09-14 |
| S02 | T1 | Dao et al., “FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness,” NeurIPS 2022 | https://papers.nips.cc/paper_files/paper/2022/hash/67d57c32e20fd0a7a302cb81d36e40d5-Abstract-Conference.html | 2026-09-14 |
| S03 | T1 | Kwon et al., “Efficient Memory Management for Large Language Model Serving with PagedAttention,” SOSP 2023 | https://doi.org/10.1145/3600006.3613165 | 2026-09-14 |
| S04 | T2 | NVIDIA CUDA Programming Guide, “The CUDA platform” | https://docs.nvidia.com/cuda/cuda-programming-guide/01-introduction/cuda-platform.html | 2026-09-14 |
| S05 | T2 | NVIDIA CUDA Programming Guide, “Compute Capabilities” | https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/compute-capabilities.html | 2026-09-14 |
| S06 | T2 | NVIDIA CUDA Compiler Driver NVCC, “GPU Compilation” | https://docs.nvidia.com/cuda/cuda-compiler-driver-nvcc/#gpu-compilation | 2026-09-14 |
| S07 | T2 | NVIDIA CUDA Compatibility | https://docs.nvidia.com/deploy/cuda-compatibility/latest/ | 2026-09-14 |
| S08 | T2 | NVIDIA Data Center Drivers, “CUDA Toolkit, Driver, and Architecture Matrix” | https://docs.nvidia.com/datacenter/tesla/drivers/cuda-toolkit-driver-and-architecture-matrix.html | 2026-09-14 |
| S09 | T2 | NVIDIA CUDA Installation Guide for Linux | https://docs.nvidia.com/cuda/cuda-installation-guide-linux/ | 2026-09-14 |
| S10 | T2 | NVIDIA CUDA Programming Guide, “CUDA Graphs” | https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/cuda-graphs.html | 2026-09-14 |
| S11 | T2 | CMake documentation, `CMAKE_CUDA_ARCHITECTURES` | https://cmake.org/cmake/help/latest/variable/CMAKE_CUDA_ARCHITECTURES.html | 2026-09-14 |
| S12 | T2 | CMake documentation, target property `CUDA_ARCHITECTURES` | https://cmake.org/cmake/help/latest/prop_tgt/CUDA_ARCHITECTURES.html | 2026-09-14 |
| S13 | T2 | CMake documentation, `FindCUDAToolkit` | https://cmake.org/cmake/help/latest/module/FindCUDAToolkit.html | 2026-09-14 |
| S14 | T3 | PyTorch official repository, source-build instructions and `CMakeLists.txt` overview | https://github.com/pytorch/pytorch | 2026-09-14 |
| S15 | T2 | PyTorch CUDA API documentation | https://docs.pytorch.org/docs/stable/cuda.html | 2026-09-14 |
| S16 | T2 | PyTorch `torch.cuda.get_device_capability` documentation | https://docs.pytorch.org/docs/stable/generated/torch.cuda.get_device_capability.html | 2026-09-14 |
| S17 | T2 | PyTorch C++/CUDA extension documentation | https://docs.pytorch.org/docs/stable/cpp_extension.html | 2026-09-14 |
| S18 | T2 | PyTorch `torch.compiled_with_cxx11_abi` documentation | https://docs.pytorch.org/docs/stable/generated/torch.compiled_with_cxx11_abi.html | 2026-09-14 |
| S19 | T2 | PyTorch `torch.export`-based ONNX exporter documentation | https://docs.pytorch.org/docs/stable/onnx_export.html | 2026-09-14 |
| S20 | T1 | ONNX Intermediate Representation specification | https://onnx.ai/onnx/repo-docs/IR.html | 2026-09-14 |
| S21 | T2 | ONNX shape-inference API | https://onnx.ai/onnx/api/shape_inference.html | 2026-09-14 |
| S22 | T2 | ONNX Runtime CUDA Execution Provider documentation | https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html | 2026-09-14 |
| S23 | T2 | ONNX Runtime TensorRT Execution Provider documentation | https://onnxruntime.ai/docs/execution-providers/TensorRT-ExecutionProvider.html | 2026-09-14 |
| S24 | T2 | NVIDIA TensorRT, “Capabilities” | https://docs.nvidia.com/deeplearning/tensorrt/latest/inference-library/capabilities.html | 2026-09-14 |
| S25 | T2 | NVIDIA TensorRT, “Dynamic Shapes: Core Concepts” | https://docs.nvidia.com/deeplearning/tensorrt/latest/inference-library/dynamic-shapes-basics.html | 2026-09-14 |
| S26 | T2 | NVIDIA TensorRT, “Version Compatibility” | https://docs.nvidia.com/deeplearning/tensorrt/10.x.x/inference-library/version-compatibility.html | 2026-09-14 |
| S27 | T2 | NVIDIA TensorRT, ONNX Opset Guide | https://docs.nvidia.com/deeplearning/tensorrt/latest/reference/onnx-opset-guide.html | 2026-09-14 |
| S28 | T3 | NVIDIA TensorRT-LLM 1.2 release notes | https://nvidia.github.io/TensorRT-LLM/1.2.0/release-notes.html | 2026-09-14 |
| S29 | T2 | NVIDIA TensorRT-LLM, “Migration Guide: TensorRT Backend Removed” | https://nvidia.github.io/TensorRT-LLM/latest/legacy/tensorrt-backend-removal.html | 2026-09-14 |
| S30 | T2 | NVIDIA TensorRT-LLM 1.2, installing on Linux with pip | https://nvidia.github.io/TensorRT-LLM/1.2.0/installation/linux.html | 2026-09-14 |
| S31 | T2 | NVIDIA TensorRT-LLM 1.2, building from source on Linux | https://nvidia.github.io/TensorRT-LLM/1.2.0/installation/build-from-source-linux.html | 2026-09-14 |
| S32 | T2 | NVIDIA TensorRT-LLM 1.2, supported hardware | https://nvidia.github.io/TensorRT-LLM/1.2.0/supported-hardware.html | 2026-09-14 |
| S33 | T2 | NVIDIA TensorRT-LLM 1.2, supported models and feature matrix | https://nvidia.github.io/TensorRT-LLM/1.2.0/models/supported-models.html | 2026-09-14 |
| S34 | T2 | NVIDIA TensorRT-LLM 1.2, architecture overview | https://nvidia.github.io/TensorRT-LLM/1.2.0/developer-guide/overview.html | 2026-09-14 |
| S35 | T2 | NVIDIA TensorRT-LLM 1.2, `trtllm-serve` | https://nvidia.github.io/TensorRT-LLM/1.2.0/commands/trtllm-serve/index.html | 2026-09-14 |
| S36 | T2 | NVIDIA TensorRT-LLM 1.2, `trtllm-bench` | https://nvidia.github.io/TensorRT-LLM/1.2.0/commands/trtllm-bench.html | 2026-09-14 |
| S37 | T3 | NVIDIA NGC TensorRT-LLM release container 1.2.0 | https://catalog.ngc.nvidia.com/orgs/nvidia/tensorrt-llm/containers/release/1.2.0/layers | 2026-09-14 |
| S38 | T2 | NVIDIA Container Toolkit installation guide | https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html | 2026-09-14 |
| S39 | T2 | Hugging Face Transformers Auto Classes documentation | https://huggingface.co/docs/transformers/model_doc/auto | 2026-09-14 |
| S40 | T3 | NVIDIA TensorRT-LLM issue #1865, T4/`sm_75` Whisper trace showing an unfused-MHA fallback in a 0.11 development build | https://github.com/NVIDIA/TensorRT-LLM/issues/1865 | 2026-09-15 |
| S41 | T3 | PyTorch `torch.cuda` source: CUDA code-image compatibility checks and published-wheel target maps | https://github.com/pytorch/pytorch/blob/main/torch/cuda/__init__.py | 2026-09-15 |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | The original Transformer replaces recurrent and convolutional sequence processing with attention-based blocks. | S01 abstract, §3 | Claim about the 2017 architecture, not every later model called a transformer |
| L02 | Scaled dot-product attention multiplies queries by transposed keys, scales by the key dimension, applies softmax, and uses the result to mix values. | S01 §3.2.1 | Mathematical definition in the original Transformer |
| L03 | FlashAttention is exact attention organized around tiling to reduce transfers between GPU high-bandwidth memory and on-chip SRAM. | S02 abstract | FlashAttention algorithm as published in 2022 |
| L04 | PagedAttention manages dynamically growing KV-cache memory in blocks inspired by virtual-memory paging. | S03 abstract and §§3–4 | PagedAttention/vLLM design; TensorRT-LLM has its own implementation |
| L05 | CUDA compute capability is a hardware feature identifier written as major.minor; the corresponding binary SM label is `sm_XY`. | S04 §1.3.1 | NVIDIA CUDA GPUs |
| L06 | Compute capability and CUDA Toolkit version are different dimensions and must not be compared as if they were the same number. | S04 §§1.3.1–1.3.2 | All CUDA deployments |
| L07 | `nvidia-smi --query-gpu=name,compute_cap` obtains the GPU name and compute capability from the installed driver. | S05 §5.1.1 | Driver/tool version that exposes `compute_cap` query |
| L08 | Compute capability can also be queried through CUDA Runtime, CUDA Driver, or NVML APIs. | S05 §5.1.1 | A process with access to a CUDA device |
| L09 | The NVIDIA driver and CUDA Toolkit are separate software products; applications need the driver at runtime, while compilation needs Toolkit tools and headers. | S04 §1.3.2; S09 §§2–3 | Native Linux CUDA development |
| L10 | The CUDA version shown by `nvidia-smi` is the maximum CUDA level supported by the driver, not proof that the matching Toolkit or `nvcc` is installed. | S08 introduction | NVIDIA data-center driver documentation; use `nvcc --version` for Toolkit discovery |
| L11 | A newer NVIDIA driver is backward compatible with applications built using an older CUDA Toolkit, while each newer Toolkit has a minimum driver requirement. | S08 introduction; S07 | Subject to NVIDIA’s documented compatibility modes and architecture support |
| L12 | CUDA Toolkit and driver releases can eventually drop code-generation or runtime support for older GPU architectures. | S08 table 3 | Architecture lifecycle varies by Toolkit and driver branch |
| L13 | `nvcc --list-gpu-arch` and `nvcc --list-gpu-code` reveal the virtual and real targets understood by that compiler. | S06 §5.7.3 | The selected `nvcc` on `PATH` |
| L14 | Repeating `--generate-code` lets one CUDA build embed cubins for several real SM targets. | S06 §5.7.3.3 | CUDA source that is valid for every requested target |
| L15 | A CUDA fatbinary may combine exact cubins with PTX, and the driver selects an appropriate image at launch. | S06 §5.6.2 | Driver supports the embedded code/PTX version |
| L16 | PTX can provide forward compatibility through driver JIT, but native cubins remain the explicit performance target. | S06 §§5.6.1–5.6.2; S17 “Compute capabilities” | Forward-compatible baseline features, not architecture-specific `a` targets |
| L17 | Architecture-specific targets introduced from compute capability 9.0 use an `a` suffix and run only on the exact architecture for which they were compiled. | S05 §5.1.2 | CUDA architecture-specific feature set |
| L18 | `CMAKE_CUDA_ARCHITECTURES` was added in CMake 3.18 and users are encouraged to set it because compiler defaults vary. | S11 lines 3–14 | CMake projects that enable CUDA |
| L19 | CMake’s `native` CUDA architecture selector was added in 3.24 and compiles for the host’s visible GPU architectures. | S12 “Special values” | Native, non-cross build with visible GPUs |
| L20 | CMake accepts `-real` and `-virtual` suffixes to request cubin and PTX code separately. | S12 lines 5–12, examples | Target `CUDA_ARCHITECTURES` property |
| L21 | `FindCUDAToolkit` can locate Toolkit libraries without enabling CUDA as a project language and exposes imported targets such as `CUDA::cudart`. | S13 overview and “Imported Targets” | CMake 3.17 or later |
| L22 | When several Toolkits are installed, `CUDAToolkit_ROOT` or an explicit compiler path avoids an ambiguous/default selection. | S13 “Search Behavior” | Hosts with multiple CUDA Toolkit installations |
| L23 | PyTorch exposes both the current device capability and the list of CUDA architectures included in the installed library. | S15 `get_arch_list`; S16 | CUDA-enabled PyTorch build and visible device |
| L24 | A useful compatibility check compares `torch.cuda.get_device_capability()` with `torch.cuda.get_arch_list()` and then launches a core CUDA operation instead of relying only on `torch.cuda.is_available()`. The architecture comparison is compatibility-aware, not a strict string-equality test. | S15; S16; S41 | Diagnostic recommendation inferred from documented APIs and current PyTorch compatibility checks |
| L25 | `TORCH_CUDA_ARCH_LIST` controls the SM targets of PyTorch CUDA extensions, and `+PTX` adds forward-compatible PTX for the named capability. | S17 “Compute capabilities” | Building a CUDA extension with PyTorch tooling |
| L26 | Compiling an extension for more architectures takes longer because a separate kernel image is generated for each target. | S17 “Compute capabilities” | PyTorch CUDA extensions |
| L27 | PyTorch’s source build is driven by its Python build frontend and CMake cache variables; invoking an arbitrary standalone `CMakeLists.txt` is not the supported top-level workflow. | S14 “From Source,” `CMakeLists.txt` build overview | Current PyTorch main build; pin the desired release tag before building |
| L28 | PyTorch CUDA source builds require a supported Toolkit, cuDNN, and a host compiler compatible with that Toolkit. | S14 “NVIDIA CUDA Support”; S09 §2 | Linux CUDA build |
| L29 | `_GLIBCXX_USE_CXX11_ABI` compatibility matters when a custom PyTorch build loads C++ extensions compiled against it. | S18; S31 overview | Linux GNU C++ ABI boundary |
| L30 | ONNX is a versioned, serialized computation-graph format; its operators are contracts, not a promise about a particular kernel implementation. | S20 “Extensible computation graph model” and “Operators” | ONNX producer/consumer boundary |
| L31 | Every ONNX model declares the operator sets it imports, and a consumer must support those operator contracts or reject the graph. | S20 “Models” and “Operators” | Standard and custom ONNX domains |
| L32 | With the `torch.export`-based exporter, `dynamic_shapes` is preferred over the older `dynamic_axes` mechanism. | S19 parameter documentation | `torch.onnx.export` with `dynamo=True` |
| L33 | ONNX shape inference can enrich `value_info`, but it may stop or fail when shapes depend on runtime data or unsupported inference rules. | S21 `infer_shapes` | Static inference pass; not execution |
| L34 | ONNX Runtime CUDA packages must match CUDA and cuDNN major-version families, and importing PyTorch first can preload compatible shared libraries. | S22 “Requirements” and “Compatibility with PyTorch” | Python environment sharing PyTorch and ONNX Runtime libraries |
| L35 | ONNX Runtime recommends registering the CUDA Execution Provider after the TensorRT provider so unsupported subgraphs can fall back to CUDA. | S23 “Usage” | ONNX Runtime using TensorRT EP |
| L36 | TensorRT commonly consumes ONNX through its parser, but ONNX support is bounded by the shipped parser’s opset and operator coverage. | S24 “Frontends”; S27 “Supported ONNX and Opset Versions” | TensorRT release selected for deployment |
| L37 | Dynamic TensorRT inputs use `-1` dimensions plus one or more optimization profiles defining minimum, optimum, and maximum shapes. | S25 “Specifying Runtime Dimensions”; S25 “Optimization Profiles” | TensorRT engines with dynamic input shapes |
| L38 | TensorRT engines are version- and GPU-specific by default; compatibility flags broaden deployment at a possible performance cost. | S26 introduction and “Hardware Compatibility” | TensorRT engine plans, not ONNX models or PyTorch checkpoints |
| L39 | TensorRT records compute capability in an engine and normally rejects deserialization when it does not match the runtime GPU. | S26 “Compatibility Checks” | Engine built without a broader hardware compatibility mode |
| L40 | In TensorRT-LLM 1.2, the legacy TensorRT engine backend was removed and PyTorch became the sole execution backend. | S28 “API Changes”; S29 “What changed” | TensorRT-LLM 1.2 and later migration path documented on 2026-09-14 |
| L41 | `trtllm-build`, checkpoint-conversion scripts, and `backend="tensorrt"` are not part of the modern TensorRT-LLM 1.2 execution path. | S29 “What changed” | TensorRT-LLM 1.2 |
| L42 | The modern `LLM` API accepts a Hugging Face model identifier or local checkpoint directly and exposes `generate()`. | S30 sanity check; S34 lines 139–148 | Supported model architecture and sufficient GPU memory |
| L43 | TensorRT-LLM 1.2’s pip guide pins PyTorch 2.9.1 with CUDA 13.0 wheels and requires a CUDA 13.1 Toolkit for that documented installation path. | S30 lines 139–163 | TensorRT-LLM 1.2 pip install on tested Ubuntu 24.04 |
| L44 | The same pip guide warns that unconstrained dependency resolution can replace an intended CUDA-enabled PyTorch build with an incompatible one. | S30 lines 211–218 | Environments where pip chooses a different torch wheel |
| L45 | NVIDIA’s prebuilt TensorRT-LLM 1.2.0 NGC image is a signed, versioned alternative to assembling the dependency matrix by hand. | S37 image metadata and layers | NGC access and compatible host driver/container runtime |
| L46 | TensorRT-LLM 1.2 documents Linux support on selected Blackwell, Hopper, Ada, and Ampere data-center systems rather than promising every NVIDIA GPU with the same SM number. | S32 lines 137–148 | Officially listed 1.2 hardware; unlisted cards require separate validation |
| L47 | TensorRT-LLM model support is architecture-specific, and advanced features vary by model family. | S33 model table and feature matrix | TensorRT-LLM 1.2 PyTorch backend |
| L48 | A Hugging Face checkpoint loading successfully in Transformers does not by itself establish that TensorRT-LLM supports its model class. | S33; S39 | Inference compatibility decision inferred from separate support registries |
| L49 | Hugging Face `AutoConfig`/Auto Classes expose the checkpoint’s resolved model architecture, which can be compared with TensorRT-LLM’s model table before loading weights. | S39 introduction and AutoConfig | Repository has a valid Transformers configuration |
| L50 | TensorRT-LLM’s executor separates scheduling, KV-cache management, model execution, and token sampling. | S34 lines 150–171 | TensorRT-LLM 1.2 architecture |
| L51 | TensorRT-LLM uses CUDA Graphs to reduce repeated CPU-side kernel-launch work in suitable inference paths. | S34 lines 172–178; S10 overview | Stable shapes/captured execution paths supported by the model configuration |
| L52 | CUDA Graphs separate definition and instantiation from repeated execution, allowing launch setup costs to be amortized. | S10 §§4.2–4.2.2 | Repeated CUDA workflows compatible with graph capture/creation |
| L53 | TensorRT-LLM’s overlap scheduler can process CPU-side results for one step while the GPU begins work for the next. | S34 lines 179–194 | Supported model/configuration in 1.2 |
| L54 | Paged KV caching allocates blocks from a managed pool and recycles them as requests progress. | S03; S34 KVCacheManager description | Conceptual mechanism; implementation details vary by server |
| L55 | `trtllm-serve` starts an OpenAI-compatible HTTP server for supported models. | S35 “About” and “Starting a Server” | TensorRT-LLM 1.2 and documented endpoints |
| L56 | TensorRT-LLM benchmarking distinguishes throughput from latency and exposes controls for concurrency, input/output lengths, warm-up, parallelism, and KV-cache allocation. | S36 throughput and latency options | Benchmark results apply only to the recorded workload and stack |
| L57 | TTFT, time per output token/inter-token latency, end-to-end latency, and token throughput measure different parts of the serving experience and should be reported together with workload shape. | S36; S35 benchmark guide | Online autoregressive serving |
| L58 | TensorRT-LLM 1.2’s source-build guide estimates about 63 GB of disk to construct its Docker image. | S31 lines 152–167 | The documented full container build |
| L59 | The source-build workflow accepts semicolon-separated CMake-style CUDA architecture targets, such as `89-real`, to reduce the compiled target set. | S31 lines 161–167 | GPU is otherwise supported by the selected TensorRT-LLM release |
| L60 | A full TensorRT-LLM source build compiles C++ and packages a wheel; a Python-only workflow can reuse precompiled native components but requires source/version alignment. | S31 “Build TensorRT LLM” | Development workflow inside the supported build environment |
| L61 | NVIDIA Container Toolkit configures Docker with `nvidia-ctk runtime configure --runtime=docker`, followed by a Docker daemon restart. | S38 “Configuring Docker” | Rootful Docker on a supported Linux distribution |
| L62 | A GPU-enabled container should be verified independently with `docker run --rm --gpus all … nvidia-smi` before blaming a framework import. | S38 “Next Steps”; NVIDIA Container Toolkit sample-workload link | Docker plus NVIDIA Container Toolkit |
| L63 | TensorRT supports multiple floating-point and integer tensor types, but hardware acceleration and model accuracy must be verified for the chosen GPU and graph. | S24 “Precision and data types” | TensorRT release/hardware/operator combination |
| L64 | The article must present ONNX→TensorRT/ONNX Runtime and TensorRT-LLM as sibling deployment branches, not as mandatory consecutive steps. | S24; S29; S30 | Modern TensorRT-LLM 1.2 baseline; inference drawn from documented workflows |
| L65 | If an old GPU architecture is absent from the selected CUDA compiler or TensorRT-LLM support list, setting a CMake SM value cannot restore removed kernels or official support. | S08 table 3; S13; S32 | Unsupported or retired architecture; conclusion follows from compiler and product support boundaries |
| L66 | If a newer GPU is visible but a PyTorch wheel has no code image compatible with it, the remedy is a matching published wheel or a source build using a Toolkit and PyTorch revision that recognize the target. | S06; S15–S17; S41 | Compatibility can exist without an exact target-string match; prove the failure with PyTorch's warning and a core CUDA operation |
| L67 | Building for the current GPU solves code-generation coverage, not missing model operators, incompatible ABIs, insufficient memory, or an unsupported TensorRT-LLM model architecture. | S17; S29; S32; S33 | Troubleshooting distinction inferred from independent compatibility layers |
| L68 | NVIDIA T4 has compute capability 7.5, expressed as `sm_75` for a real CUDA binary target. | S05 compute-capability tables | Hardware identity; not a claim that every current framework release validates T4 |
| L69 | A historical TensorRT-LLM T4 trace shows the runtime recognizing `sm_75` and selecting an unfused MHA fallback when a fused path did not support the configuration. | S40 issue trace | TensorRT-LLM 0.11.0 development build and Whisper; evidence of a fallback path, not proof of TensorRT-LLM 1.2 support or a successful end-to-end run |
| L70 | Absence from TensorRT-LLM 1.2's validated-hardware list is not proof that inference is physically impossible; it means NVIDIA does not make the same release-specific validation claim for that device, so any working configuration must be reported with exact versions and observed limitations. | S32; S40; project-owner field report | The distinction between official validation and observed execution is an inference; it must not be rewritten as official support |
| L71 | Rebuilding one CUDA extension is insufficient when the installed PyTorch binary itself lacks any executable code compatible with the device, such as a pinned release that cannot execute a core operation on `sm_121`; after confirming that the chosen CUDA Toolkit and PyTorch revision understand the SM, a full PyTorch source build is then the smallest valid PyTorch-layer repair. | S06; S14–S17; S41 | Do not infer this condition merely because `sm_121` is absent from `get_arch_list()`; a compatible 12.x image may cover the device |
| L72 | Current PyTorch source checks code-image compatibility rather than requiring the device's exact SM string, and its warning distinguishes “this installed build lacks kernels” from “another published CUDA build may cover the GPU.” | S41 lines 2693–2954 as accessed | Current main-branch diagnostic behavior; pin the release because these maps evolve |

## What the post can honestly claim

1. Compatibility is not one version comparison. It is the intersection of CPU/OS, GPU compute capability, driver, Toolkit/compiler, native library ABI, PyTorch binary targets, model implementation, and runtime memory.
2. A reproducible audit can detect each layer before downloading a model: host architecture, visible GPUs and SMs, driver ceiling, `nvcc` target support, CMake selection, PyTorch cubins/PTX, C++ ABI, and model class.
3. A small, modern `CMakeLists.txt` can compile a CUDA probe for an explicit `CMAKE_CUDA_ARCHITECTURES` value and fail early when the compiler does not recognize the requested target.
4. The repair ladder has three explicit rungs: rebuild one out-of-tree CUDA extension when only that extension lacks the target; rebuild PyTorch itself when its warning and a core CUDA operation prove that the installed wheel has no compatible code image for the device (the conditional `sm_121` case); rebuild TensorRT-LLM only when its native components, rather than PyTorch, are the uncovered layer. Every rung is conditional on the selected compiler and source revisions recognizing that SM.
5. For stable TensorRT-LLM 1.2, the executable tutorial should use the PyTorch-backed `LLM`/`trtllm-serve` APIs directly from a supported Hugging Face checkpoint. It should not teach the removed `trtllm-build` workflow.
6. ONNX belongs in a separate deployment branch for graphs intended for TensorRT or ONNX Runtime. It remains valuable, but it is not a prerequisite for modern TensorRT-LLM.
7. The safest first run is the signed, versioned NVIDIA release container, followed by a source-build path only for debugging, ABI requirements, or explicit CUDA-target control.
8. An unlisted GPU can still execute a particular TensorRT-LLM/model/version combination. The article will distinguish that observed result from NVIDIA's narrower release-validation statement, include the T4 field experience with an explicit qualification, and never turn one working run into a general support claim.
9. Performance claims should be generated on the reader’s hardware and workload, reporting TTFT, TPOT/ITL, end-to-end latency, throughput, input/output lengths, concurrency, precision, and memory settings. The post will not repeat vendor headline benchmarks as universal results.

## Contested, superseded, or version-sensitive material

- Many still-indexed TensorRT-LLM tutorials describe checkpoint conversion, `trtllm-build`, and serialized TensorRT engines. Those instructions are legacy for the 1.2 baseline because NVIDIA removed that backend. The article will label the history but will not make old commands the happy path.
- NVIDIA’s TensorRT-LLM 1.2 pip page documents PyTorch 2.9.1, while parts of the 1.2 source-build page contain broader or older wording about PyTorch versions. The executable path will pin the complete 1.2 release container; any bare-metal path will print and record installed versions rather than mix snippets.
- Generic TensorRT hardware support is broader than the TensorRT-LLM 1.2 supported-hardware page. The article will never infer TensorRT-LLM support merely from TensorRT accepting the GPU’s SM.
- Conversely, omission from TensorRT-LLM's validated-hardware page will not be described as a physical inability to execute. The T4 section will separate three statements: NVIDIA's 1.2 validation list, historical evidence of `sm_75` fallback behavior, and the project owner's field report of successful inference on smaller-SM hardware.
- PTX improves forward compatibility but is not equivalent to a native cubin for the new device, and architecture-specific `a` targets deliberately narrow portability.
- ONNX opset support changes with exporters and TensorRT/ONNX Runtime releases. The article will inspect the produced model and parser rather than hard-code one supposedly universal opset.

## Open questions

- TensorRT-LLM 1.2’s official hardware page lists selected products rather than a complete SM-by-SM execution contract. The post will say that an unlisted T4 may run a compatible path, then require an exact-version smoke test and label the result “observed working on this stack,” not “officially supported by 1.2.”
- “L4” means the blog-forge L4 depth tier. The hardware correction is NVIDIA T4 (`sm_75`), not NVIDIA L4. The exact successful T4 field stack (TensorRT-LLM, CUDA, PyTorch, model, and precision) is not yet recorded, so it will be an explicitly attributed field note rather than a reproducible benchmark claim.
- No benchmark numbers will be claimed until they are measured on a specified GPU, model revision, precision, request distribution, and concurrency. The tutorial will provide the harness and reporting table instead.
- Source-building all of PyTorch is expensive but is the intended repair when the PyTorch binary itself cannot run a core operation on a new device such as `sm_121` and no matching upstream wheel is available. The article must compare device capability, compiler targets, PyTorch's compatibility warning, `torch.cuda.get_arch_list()`, and a synchronized core operation before starting the build; absence of the literal `sm_121` string alone is not sufficient.
