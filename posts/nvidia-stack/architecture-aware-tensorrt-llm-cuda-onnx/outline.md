# Outline — From PyTorch Tensors to TensorRT-LLM

## Article contract

- **Depth:** L4 pillar
- **Target length:** 9,440 words (acceptable range: 7,500–10,000)
- **Target reader:** senior ML/inference engineers who can use Linux, Python environments, Docker, and CMake but need a rigorous mental model for CUDA architecture compatibility
- **Worked systems:** NVIDIA T4 (`sm_75`) as an older, unlisted TensorRT-LLM 1.2 case; a CUDA 12.1-capability device (`sm_121`) as a newer device whose installed PyTorch wheel may lack binary coverage
- **Version policy:** executable TensorRT-LLM instructions are pinned to stable 1.2.0; historical evidence is labeled with its original version
- **Benchmark policy:** publish the harness and schema, not invented results. Any filled value must record GPU, driver, Toolkit, framework versions, model revision, precision, input/output distribution, concurrency, warm-up, and memory settings.

## Narrative spine

The article opens with two machines that can produce similar CUDA launch errors for opposite reasons. On the T4, a modern product release may no longer validate or ship every optimized path even though some inference configurations can execute through compatible or fallback kernels. On an `sm_121` device, the hardware can be newer than the PyTorch wheel's compatible code-image set, so rebuilding PyTorch itself can be the correct repair after a newer matching wheel is ruled out. The reader audits the stack from hardware upward, chooses the lowest broken layer, and finishes with two honest deployment branches: modern PyTorch-backed TensorRT-LLM, or ONNX feeding TensorRT/ONNX Runtime.

## Section outline and word budget

### 1. Key insights — 240 words

- **Job:** give the conclusions before the machinery.
- **Reader can:** distinguish compute capability from Toolkit version; identify the three rebuild scopes; understand that “validated,” “can execute,” and “fast” are different claims; avoid inserting ONNX into TensorRT-LLM 1.2's direct path.
- **Claims:** L05–L06, L24, L40–L41, L64, L70–L71.
- **Sources:** S04–S06, S15–S17, S28–S32.
- **Figures:** none; preserve a fast opening.

### 2. Who this is for — 130 words

- **Job:** define prerequisites, machines in scope, and what the article will not promise.
- **Reader can:** decide whether to follow the complete build path or use only the audit/repair decision tree.
- **Claims:** L09, L28, L62.
- **Sources:** S04, S09, S14, S38.
- **Figures:** none.

### 3. Why architecture awareness matters — 330 words

- **Job:** replace “CUDA version mismatch” with a layered compatibility model.
- **Reader can:** locate a failure among driver, Toolkit, code image, PyTorch, model integration, and serving runtime.
- **Claims:** L05–L17, L38–L39, L67.
- **Sources:** S04–S08, S17, S26.
- **Figures:** F01 compatibility stack; F02 compute-capability-versus-Toolkit axes.

### 4. The problem: one error, two opposite machines — 650 words

- **Job:** set up the T4 and `sm_121` cases without prematurely prescribing a build.
- **Reader can:** explain why an old/unlisted device and a new/uncovered device can both surface “no kernel image,” unsupported-architecture warnings, or missing-kernel paths.
- **Claims:** L10–L17, L23–L24, L43–L46, L65–L71.
- **Sources:** S05–S08, S15–S17, S30–S32, S40.
- **Required nuance:** quote no more than a short error fragment. State that the project owner reports successful smaller-SM inference; distinguish that field observation from 1.2 official validation. State that S40 demonstrates an `sm_75` fallback decision in a historical development version, not successful 1.2 inference.
- **Figures:** F03 two-host comparison; F04 fatbinary/cubin/PTX selection.

### 5. Worked example: audit before rebuilding — 1,180 words

- **Job:** walk both hosts through the same read-only audit and obtain two different diagnoses.
- **Reader can:** record OS/CPU, GPU and SM, driver ceiling, actual `nvcc`, compiler-supported targets, CMake selection, PyTorch device visibility, PyTorch compiled architectures, ABI, and model class.
- **Claims:** L07–L13, L18–L24, L29, L44, L48–L49, L62.
- **Sources:** S05–S09, S11–S18, S30, S33, S38–S39.
- **Executable artifacts planned:** `audit_stack.sh` and `audit_torch.py`; outputs are illustrative schemas rather than fabricated machine results.
- **Decision result:**
  - T4: `sm_75` is known hardware; the next question is whether the pinned CUDA/framework/product versions retain a usable path.
  - `sm_121`: if the chosen compiler recognizes 12.1, PyTorch reports that no compatible code image exists, and a synchronized core CUDA operation fails, the installed PyTorch binary is the uncovered layer. A missing literal `sm_121` entry alone is not proof because another compatible 12.x image may cover it.
- **Figures:** F05 audit decision tree; F06 device-SM versus PyTorch-binary-coverage diagnostic.

### 6. Intuition: architecture targets are executable inventory — 790 words

- **Job:** explain CUDA code images deeply enough that CMake and PyTorch settings stop looking like magic flags.
- **Reader can:** reason about real cubins, virtual PTX, driver JIT, fatbinaries, exact architecture-specific targets, and why compiling more targets increases build time.
- **Claims:** L13–L20, L25–L26.
- **Sources:** S05–S06, S11–S12, S17.
- **Figures:** F07 code-image selection path; F08 CMake target notation map.

## Body

### 7. Audit the compatibility stack from the bottom up — 500 words

- **Job:** turn the worked example into a reusable checklist with stop conditions.
- **Reader can:** prove each prerequisite before installing or compiling the next layer.
- **Claims:** L09–L13, L21–L24, L44, L61–L62.
- **Sources:** S04, S06–S09, S13, S15–S16, S30, S38.
- **Figures:** F09 compatibility evidence matrix.

### 8. Choose the smallest valid repair — 640 words

- **Job:** make the rebuild scopes mutually clear.
- **Reader can:** choose among:
  1. rebuild only one PyTorch/CUDA extension with `TORCH_CUDA_ARCH_LIST`;
  2. rebuild PyTorch when its own binary lacks the device target;
  3. rebuild TensorRT-LLM when its native components are the uncovered layer;
  4. pin an older compatible stack or use another runtime when the selected release removed the architecture/path.
- **Claims:** L25–L29, L58–L60, L65–L71.
- **Sources:** S08, S14, S17–S18, S31–S33.
- **Hard guardrail:** a CMake flag cannot manufacture product support, missing operators, memory, or a model adapter.
- **Figures:** F10 repair ladder.

### 9. Build PyTorch for an uncovered `sm_121` target — 710 words

- **Job:** present the expensive path only after its preconditions are proven.
- **Reader can:** first rule out a compatible published wheel, then pin a PyTorch revision, verify its source recognizes 12.1, select a compatible Toolkit/host compiler/cuDNN, set `TORCH_CUDA_ARCH_LIST`, build through PyTorch's supported frontend, install into an isolated environment, and verify target/ABI/runtime behavior.
- **Claims:** L17, L27–L29, L66–L71.
- **Sources:** S05–S06, S09, S14, S17–S18.
- **Safety notes:** do not call an arbitrary top-level CMake invocation the supported PyTorch build; record build provenance; keep the previous environment recoverable; do not assume target recognition on every older PyTorch tag.
- **Figures:** F11 full-PyTorch source-build pipeline.

### 10. Check transformer and model support separately — 450 words

- **Job:** show that successful CUDA code generation is necessary but not sufficient for an LLM.
- **Reader can:** resolve a Hugging Face model class, compare it with TensorRT-LLM's release table, estimate KV-cache pressure, choose a precision the GPU/runtime can execute, and detect unsupported feature combinations.
- **Claims:** L01–L04, L47–L54, L63, L67.
- **Sources:** S01–S03, S10, S24, S33–S34, S39.
- **Figures:** F12 transformer tensor/KV-cache flow; F13 model-support gates.

### 11. Choose the deployment branch: TensorRT-LLM or ONNX — 480 words

- **Job:** correct the common belief that modern TensorRT-LLM requires an ONNX intermediate.
- **Reader can:** select direct Hugging Face/PyTorch-backed TensorRT-LLM for supported generative models, or export ONNX for generic TensorRT/ONNX Runtime consumption.
- **Claims:** L30–L41, L64.
- **Sources:** S19–S29.
- **Figures:** F14 sibling deployment branches.

### 12. Install and run TensorRT-LLM 1.2 honestly — 520 words

- **Job:** provide a container-first smoke test, a pinned pip alternative, and a narrowly justified source build.
- **Reader can:** verify GPU container access, launch a supported Hugging Face model via `LLM.generate()`, start `trtllm-serve`, and interpret an unlisted T4 result without overstating support.
- **Claims:** L40–L46, L55, L58–L62, L68–L70.
- **Sources:** S28–S32, S35, S37–S38, S40.
- **T4 wording rule:** “observed working for this exact stack” is permitted when backed by a reproduced run; “TensorRT-LLM 1.2 supports T4” is not supported by S32. A failed optimized kernel may have a fallback, or may be terminal—test the specific model/precision/version.
- **Figures:** F15 validation-versus-execution matrix.

## The math

### 13. Attention shapes, KV-cache bytes, and why memory gates inference — 760 words

- **Job:** connect tensors to serving constraints without turning the article into a transformer primer.
- **Reader can:** verify Q/K/V and attention output shapes; calculate KV-cache storage from layers, KV heads, head dimension, tokens, batch/concurrency, and bytes per element; understand why grouped-query attention and quantized cache change the budget.
- **Claims:** L02–L04, L47, L50, L54, L63.
- **Sources:** S01–S03, S24, S33–S34.
- **Equations planned:**
  - `QK^T / sqrt(d_k)` shape path;
  - approximate KV bytes `2 × layers × tokens × kv_heads × head_dim × bytes_per_element × active_sequences`;
  - a transparent usable-memory budget that leaves room for weights, activations, workspaces, and runtime overhead.
- **Figures:** reuse F12; no decorative equation image.

## Implementation

### 14. Reproducible files and commands — 790 words

- **Job:** consolidate the runnable pieces in dependency order.
- **Reader can:** run:
  1. host/PyTorch audit;
  2. an explicit CUDA CMake probe using real/virtual targets;
  3. an extension-only rebuild;
  4. the gated PyTorch source build;
  5. TensorRT-LLM 1.2 direct generation and serving;
  6. a separate `torch.export`-based ONNX export with dynamic shapes;
  7. ONNX checking/shape inference and TensorRT or ONNX Runtime provider selection;
  8. a benchmark harness that reports latency and throughput without pre-filled results.
- **Claims:** L18–L45, L55–L60, L64, L71.
- **Sources:** S11–S31, S35–S36.
- **Planned files:** `examples/audit_stack.sh`, `examples/audit_torch.py`, `examples/cuda_probe/CMakeLists.txt`, `examples/cuda_probe/probe.cu`, `examples/export_onnx.py`, `examples/run_trtllm.py`, `examples/benchmark.sh`, and `examples/benchmark-report.md`.
- **Figures:** F16 benchmark-event timeline.

## Limitations and failure modes

### 15. What a successful build still does not prove — 470 words

- **Job:** prevent target compilation from being mistaken for correctness, support, or performance.
- **Reader can:** recognize removed old-SM compiler support, PTX JIT limits, `a`-target non-portability, ABI conflicts, parser/operator gaps, dynamic-shape profile errors, engine/GPU mismatch, unsupported model features, OOM, inaccurate quantization, and pip dependency replacement.
- **Claims:** L12, L16–L17, L29–L39, L44, L47–L49, L63, L65–L70.
- **Sources:** S05–S08, S18–S27, S30, S32–S33, S40.
- **Figures:** reuse F09/F10/F15 as troubleshooting references.

## Takeaways

### 16. The five rules to keep — 210 words

- **Job:** compress the article into an operational policy.
- **Reader can:** audit, identify the uncovered layer, make the smallest build, select the correct deployment branch, and report observed behavior without inflating it into universal support.
- **Claims:** synthesis of L24, L40–L46, L64–L71.
- **Figures:** none.

## Try it yourself

### 17. A controlled lab sequence — 230 words

- **Job:** give the reader a low-risk order of experiments.
- **Reader can:** run the audit; build the tiny CMake probe; compare extension-only versus framework-level coverage; perform the container smoke test; fill the benchmark report on an exact stack.
- **Success criterion:** every conclusion is backed by a captured command/output or a versioned official support statement.
- **Figures:** none.

## References — 360 words

- **Job:** provide grouped links for CUDA/CMake, PyTorch, ONNX/TensorRT, TensorRT-LLM, and transformer foundations.
- **Source policy:** use the 40-entry ledger selectively; cite the closest primary/official page at each technical assertion and label S40 as issue/field evidence.
- **Figures:** none.

## Word-budget check

| Block | Words |
|---|---:|
| Key insights through intuition | 3,320 |
| Six body sections | 3,300 |
| The math | 760 |
| Implementation | 790 |
| Limitations | 470 |
| Takeaways, lab, references | 800 |
| **Planned total** | **9,440** |

The target remains inside the L4 range. During drafting, compress repeated explanation in the worked example/body overlap if needed, without deleting the repair decision logic.

## Figure plan (18 figures)

| ID | Section | One thing the figure must teach | Route | Draft caption |
|---|---|---|---|---|
| F01 | Why it matters | A CUDA inference result is the intersection of multiple compatibility layers. | diagram-design | **Compatibility is a stack, not a version number.** A green GPU check does not prove that the compiler, PyTorch binary, model adapter, and serving runtime all cover the same device. |
| F02 | Why it matters | Compute capability and CUDA Toolkit release are independent axes. | diagram-design | **Do not compare `sm_121` with “CUDA 12.1.”** The former identifies a hardware feature level; the latter names a software release family. |
| F03 | Problem | T4 and an `sm_121` device can show similar symptoms for opposite lifecycle reasons. | diagram-design | **Same launch symptom, opposite diagnosis.** The T4 may be outside a release's validated/optimized set; the new device may be ahead of the installed wheel's binary targets. |
| F04 | Problem | The driver selects an exact cubin when possible, otherwise compatible PTX may JIT, otherwise launch fails. | diagram-design | **What the CUDA driver can actually launch.** A visible device is useful only when the process contains a compatible code image. |
| F05 | Worked example | The audit order and its stop conditions. | Mermaid → diagram-design | **Audit before compiling.** Each check narrows the repair from product choice down to one binary target. |
| F06 | Worked example | Combine device capability, PyTorch code-image inventory, compatibility rules, warnings, and a real core operation. | diagram-design | **The decisive PyTorch test is not string equality.** `get_device_capability()` describes hardware, `get_arch_list()` describes the binary, and an actual synchronized operation proves whether they work together. |
| F07 | Intuition | Relationship among CUDA source, virtual architecture/PTX, real architecture/cubin, fatbinary, and JIT. | diagram-design | **From source to executable GPU inventory.** Real and virtual targets provide different portability and performance properties. |
| F08 | Intuition | Map CMake values such as `75-real`, `121-real`, and virtual targets to emitted code. | diagram-design | **CMake architecture notation made explicit.** Target properties should say which cubins and PTX the artifact is meant to carry. |
| F09 | Audit body | Evidence matrix across host, driver, Toolkit, compiler, PyTorch, model, and runtime. | diagram-design | **Every layer needs its own evidence.** The matrix prevents one successful command from being used as proof for the whole stack. |
| F10 | Failure ownership | Each failure phase — configure, import, first synchronised op, model load, request — is owned by a different artifact. | diagram-design | **Where it failed names what to repair.** The phase that produced the first precise error identifies the artifact, and rules out the reflex repair that changes something else. |
| F11 | Repair ladder | Choose extension rebuild, PyTorch rebuild, TensorRT-LLM rebuild, or a different/pinned runtime. | Mermaid → diagram-design | **Repair the lowest broken layer.** A full framework build is justified only when smaller artifacts cannot supply the missing code. |
| F12 | PyTorch build | Supported PyTorch build frontend driving CMake/Ninja/NVCC and producing a versioned wheel. | diagram-design | **A PyTorch source build is a wheel-production pipeline.** Pin sources, feed supported build variables, and verify the installed result. |
| F13 | Model support | Q/K/V tensor shape flow and the per-layer growth of the KV cache during decoding. | diagram-design | **Why autoregressive inference keeps state.** Each generated token extends key/value storage across layers and active sequences. |
| F14 | Model support | CUDA coverage, model-class integration, feature/precision availability, and memory are separate gates. | diagram-design | **A compiled kernel is only the first gate.** The model still needs a supported adapter, feature combination, precision, and enough memory. |
| F15 | Deployment choice | Modern TensorRT-LLM direct path and ONNX→TensorRT/ORT are sibling branches. | Mermaid → diagram-design | **ONNX is a branch, not a required TensorRT-LLM stage.** Choose the interchange path according to the target runtime. |
| F16 | TensorRT-LLM/T4 | Separate official validation, observed execution, optimized-kernel availability, and fallback behavior. | diagram-design | **“Runs” and “supported” answer different questions.** Record the exact working stack without extending NVIDIA's published validation claim. |
| F17 | The math | Only the KV term scales with admitted concurrency; the fixed terms do not move. | diagram-design | **Only the cache scales with concurrency.** At a fixed configuration the cache costs a flat amount per resident sequence, so admission alone decides whether the same model still fits. |
| F18 | Implementation/benchmark | Timeline from request arrival through TTFT, inter-token intervals, completion, and aggregate throughput. | diagram-design | **Measure the serving experience, not one headline number.** TTFT, TPOT/ITL, end-to-end latency, and throughput describe different bottlenecks. |

## Drafting guardrails

- Do not conflate NVIDIA T4 with NVIDIA L4; “L4” in the brief is the article depth.
- Do not say TensorRT-LLM 1.2 officially supports T4. Say the official 1.2 list omits it, while exact older or field-tested stacks can still execute some model paths.
- Do not claim S40 proves successful end-to-end inference; it proves a historical T4 code path reached a documented fallback decision.
- Do not tell a reader to build PyTorch until its warning and a core CUDA operation prove that the wheel—not merely one extension—lacks a compatible local code image.
- Do not use `TORCH_CUDA_ARCH_LIST` as if it overrode an NVCC or source tree that does not recognize the target.
- Do not present removed `trtllm-build`/TensorRT-engine-backend instructions as current for 1.2.
- Do not place ONNX between Hugging Face and TensorRT-LLM 1.2.
- Do not publish benchmark values without the full reproducibility tuple.

## Checkpoint B

Await approval of this outline, repair ladder, T4 wording, word budget, and 18-figure plan before drafting `blog.md` or rendering assets.
