# Series plan — The NVIDIA Stack

**Slug:** nvidia-stack · **Shape:** hybrid · **Parts:** 16 (15 committed, 1 optional)

## Why this is a series and not one post

Two different seams force the split. The first is a real prerequisite seam: nothing about
compilation targets, profiling, or why a serving engine ran out of memory can be explained until
the reader accepts that "CUDA" is five separately versioned artifacts rather than one product,
and that acceptance is itself a post. The second is a decomposition seam: once the platform map
and the execution model exist, the regions of that map — kernels, profiling, compatibility
repair, memory sizing, quantization, serving, multi-GPU, training at scale, edge — are disjoint
enough that each is its own 4,000–10,000-word post with its own search intent. Budgeting the
whole thing as one article gives roughly 100,000 words and 190 figures.

So this is a **hybrid**: a three-rung ladder (Parts 1 → 2 → 3) whose top rung fans out into
thirteen sibling spokes. Parts 1–3 cover the same territory at rising depth; Parts 4–16 cover
disjoint territory, each at the depth its own subject needs.

## The angle, and why it is not a CUDA tutorial

The scoping sweep found that introductory CUDA is the most saturated ground in the entire
subject: NVIDIA's own *An Even Easier Introduction to CUDA*, the CUDA C++ Programming Guide, the
Best Practices Guide, the Nsight Compute Profiling Guide, Cornell Virtual Workshop, the PMPP
book and a dozen course repos already own hello-world, the threads/blocks/grids diagram, the
optimization checklist and the metric dictionary. A post that restates any of them is worthless.

What is *not* owned is the failure surface and the decision surface. The sweep measured roughly
3,300 open GitHub issues containing `no kernel image is available for execution` and roughly
3,400 containing `device-side assert triggered`, against top search results that are
auto-generated three-bullet SEO pages. So every part in this series is built on one of three
shapes, never on a feature tour:

- **a failure that shares one error message with four unrelated causes** (Parts 2, 4, 6, 14),
- **a decision an engineer has to defend** (Parts 9, 10, 11, 12, 13, 15),
- **a mechanism whose canonical explanation is now a generation out of date** (Parts 7, 8).

## Reader objectives

| # | After this the reader can ... | Part |
|---|---|---|
| 1 | name every layer between a Python tensor call and a SASS instruction, and say which vendor artifact owns each | 1 |
| 2 | say what CUDA-X is, and which of its libraries they are already using without having installed one | 1 |
| 3 | decide whether a given task needs the Toolkit, a framework wheel, a container, or nothing | 1 |
| 4 | explain why `nvidia-smi` and `nvcc --version` disagree, and say which one is a lie about what is installed | 2 |
| 5 | state the minor-version compatibility rule and when the forward-compatibility package applies | 2 |
| 6 | predict whether a given wheel will run on a given driver before installing it | 2 |
| 7 | say why 100% in `nvidia-smi` utilization does not mean the GPU is busy | 3 |
| 8 | find the host-side sync point that is serialising an otherwise asynchronous pipeline | 3 |
| 9 | say what CUDA Graphs remove and what they cannot remove | 3 |
| 10 | tell five different causes of one `CUDA out of memory` message apart from the traceback alone | 4 |
| 11 | read `reserved` versus `allocated` and decide whether the problem is capacity or fragmentation | 4 |
| 12 | get from "the model is slow" to a named bottleneck without guessing | 5 |
| 13 | decide whether the time is even on the GPU before opening a kernel profiler | 5 |
| 14 | read a roofline chart and say which side of the ridge a kernel sits on | 5 |
| 15 | audit a broken stack bottom-up and assign the failure to exactly one artifact | 6 |
| 16 | choose the smallest valid repair instead of rebuilding the framework by reflex | 6 |
| 17 | say what a fatbinary contains and how the driver picks an image out of it | 6 |
| 18 | say what changes in their code between two GPU generations, without reading a spec table | 7 |
| 19 | explain why four mutually incompatible compilation targets ship under one architecture brand | 7 |
| 19a | say why a numerically higher compute capability can lack a feature a lower one has | 7 |
| 20 | reason about coalescing and bank conflicts in the TMA era rather than the Kepler era | 8 |
| 21 | say when the classic shared-memory padding trick is now the wrong answer | 8 |
| 22 | pick between CUDA C++, Triton, CuTe DSL and cuTile for one specific kernel | 9 |
| 23 | say what each of those four costs in time-to-working and in achieved bandwidth | 9 |
| 24 | distinguish weight-only quantization from math the tensor cores actually execute | 10 |
| 25 | say which numeric formats a given GPU generation can execute rather than emulate | 10 |
| 26 | compute the KV cache correctly for a GQA, MQA or MLA model instead of assuming MHA | 11 |
| 27 | explain why a serving engine reports zero free VRAM by design | 11 |
| 28 | characterise their own traffic well enough to choose a serving engine on evidence | 12 |
| 29 | say what Triton, Dynamo, Dynamo-Triton, NIM and TensorRT-LLM each are and which wraps which | 13 |
| 30 | tell an NCCL hang apart from a data-loader stall before touching an environment variable | 14 |
| 31 | read an `NCCL_DEBUG=INFO` transcript and say which transport was actually selected | 14 |
| 32 | order parallelism strategies by communication volume and map them onto the interconnect | 15 |
| 33 | say why turning on FP8 training frequently makes a job slower | 15 |
| 34 | predict which component pins which on a Jetson, from the failure signature | 16 |

## Parts

### Part 1 — What the NVIDIA Stack Actually Is

- **Slug:** what-the-nvidia-stack-actually-is
- **Tier:** L2 · **Difficulty:** beginner · **Est. words:** 4,000 · **Figures:** 7
- **Answers:** what are all these products, and which of them do I actually need?
- **Assumes:** Python, a shell, and knowing that a GPU exists. No CUDA, no C++.
- **Owns:** the layer map — kernel driver, `libcuda.so` driver API, CUDA runtime, Toolkit and
  `nvcc`, CUDA-X libraries, frameworks, serving products — and the rule for which layer a given
  task touches.
- **Hands off:** the version arithmetic to Part 2; the execution model to Part 3; every
  individual product to its own spoke.
- **Worked example:** one `torch.randn(...).cuda() @ w` traced downward through every layer it
  touches, naming the artifact and the file on disk at each step, ending at a cuBLAS kernel.
- **Key sources:** CUDA Toolkit documentation index; the CUDA-X product pages; the PyTorch
  wheel's bundled-library listing. Pin versions at research time, not now.
- **Search intent:** "nvidia software stack explained", "what is CUDA-X", "do I need to install
  CUDA toolkit for pytorch", "difference between CUDA and cuDNN"

### Part 2 — The Four CUDA Version Numbers

- **Slug:** four-cuda-version-numbers
- **Tier:** L2 · **Difficulty:** intermediate · **Est. words:** 4,500 · **Figures:** 8
- **Answers:** which CUDA do I have, and which of these numbers decides whether my code runs?
- **Assumes:** Part 1's layer map — the `#the-layer-map` anchor. Re-states it in three sentences,
  no more.
- **Owns:** kernel driver vs `libcuda.so` vs the runtime bundled in a wheel vs Toolkit `nvcc` vs
  the framework's build-time CUDA; minor-version compatibility; the forward-compatibility
  package and its actual preconditions.
- **Hands off:** compute capability and fatbinaries to Part 6 — this part deliberately stops at
  *version* compatibility and does not touch *architecture* compatibility.
- **Worked example:** one machine, five commands, five different version numbers printed side by
  side, each traced to the artifact that produced it and to what it does and does not promise.
- **Key sources:** the CUDA Compatibility document (cite the rules; never restate the matrix);
  driver release notes; the framework wheel's metadata.
- **Search intent:** "nvidia-smi shows different CUDA version than nvcc", "which CUDA version do
  I have", "do I need the CUDA toolkit for pytorch", "CUDA driver compatibility"

### Part 3 — Why Your GPU Is Idle at 100% Utilization

- **Slug:** gpu-idle-at-100-percent-utilization
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,000 · **Figures:** 10
- **Answers:** the GPU reports 100% busy and the job is slow — where is the time actually going?
- **Assumes:** Part 1's layer map. Python, and what a thread is.
- **Owns:** the asynchronous execution model — launch queues, streams, events, the host-side sync
  points that quietly serialise everything, launch overhead, and what CUDA Graphs do and do not
  remove. Establishes that `nvidia-smi` utilization means "at least one kernel was resident
  during the sample window", not "the SMs were busy".
- **Hands off:** the profiler workflow to Part 5; kernel-internal memory behaviour to Part 8.
- **Worked example:** one small training step where more than half the wall clock is host-side,
  shown twice — once with a naive timing loop that reports the wrong answer because it forgot to
  synchronise, then with events that report the right one.
- **Key sources:** CUDA C++ Programming Guide on streams and graphs; the `nvidia-smi` utilization
  field definition; Nsight Systems documentation on the timeline rows.
- **Search intent:** "nvidia-smi 100% utilization but slow", "is my code actually running on the
  GPU", "CUDA synchronize timing", "what do CUDA graphs actually speed up"

### Part 4 — Five Causes of One "CUDA Out of Memory"

- **Slug:** five-causes-of-cuda-out-of-memory
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 5,500 · **Figures:** 9
- **Answers:** the message is always the same — how do I tell which of five unrelated problems I
  have?
- **Assumes:** Part 3's asynchronous execution model, for why a freed tensor is not free yet.
- **Owns:** the caching allocator, `reserved` vs `allocated`, fragmentation and
  `expandable_segments`, a retained autograd graph, a second process or zombie holding VRAM, and
  non-PyTorch allocations (NCCL buffers, cuBLAS workspaces, the CUDA context itself). One
  decision tree that maps the observable evidence to exactly one cause.
- **Hands off:** serving-time capacity planning to Part 11 — this part is about diagnosing a
  crash, not about sizing a deployment.
- **Worked example:** the same 20 GiB model failing five times for five different reasons, with
  the allocator summary printed after each, and the one number that discriminates each case.
- **Key sources:** PyTorch CUDA caching-allocator documentation and memory-snapshot tooling;
  `PYTORCH_CUDA_ALLOC_CONF` reference; the allocator source for the release being written about.
- **Search intent:** "CUDA out of memory but GPU is empty", "reserved but unallocated memory is
  large", "PYTORCH_CUDA_ALLOC_CONF expandable_segments", "torch.cuda.OutOfMemoryError"

### Part 5 — Reading a GPU Profile

- **Slug:** reading-a-gpu-profile
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,500 · **Figures:** 11
- **Answers:** how do I get from "it's slow" to a named bottleneck without guessing?
- **Assumes:** Part 3's execution model — the `#host-side-sync-points` anchor.
- **Owns:** the workflow, not the metric dictionary. Nsight Systems first to decide whether the
  time is even on the GPU; only then Nsight Compute on the one kernel that matters; roofline
  reading; why low occupancy is often the correct answer and not a bug.
- **Hands off:** fixing what the profile reveals to Parts 8 and 9.
- **Worked example:** one genuinely slow model profiled start to finish, where the first profile
  shows the bottleneck is the data loader and the GPU work is not the problem at all — then a
  second pass after that is fixed, which finally earns a kernel profile.
- **Key sources:** Nsight Systems and Nsight Compute user guides (cite for definitions, never
  restate the counter dictionary); the roofline model's original paper; CUPTI documentation.
- **Search intent:** "Nsight Compute how to read roofline", "is my kernel memory bound or compute
  bound", "Nsight Systems vs Nsight Compute", "how to profile pytorch GPU"

### Part 6 — CUDA Architecture Repairs: PyTorch, TensorRT-LLM, ONNX

- **Slug:** architecture-aware-tensorrt-llm-cuda-onnx
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,024 (drafted) · **Figures:** 18
- **Answers:** two machines throw the same launch error for opposite reasons — which layer is
  actually broken, and what is the smallest repair?
- **Assumes:** Part 2's version model — the `#the-five-version-numbers` anchor. Linux, Python
  environments, CMake, Docker, transformer basics.
- **Owns:** compute capability as a hardware fact; fatbinaries as executable inventory (real
  cubins, virtual PTX, driver-side image selection, JIT); `nvcc` gencode and CMake
  `CUDA_ARCHITECTURES`; the eight-row audit matrix; failure-phase-to-artifact ownership; the
  five-rung repair ladder; the four model-support gates; TensorRT-LLM and ONNX as sibling
  branches rather than a pipeline; attention shapes and KV-cache capacity.
- **Hands off:** architecture *generations* and their porting consequences to Part 7; serving
  engine choice to Part 12; the NVIDIA serving product map to Part 13; deployment-time VRAM
  sizing to Part 11.
- **Worked example:** an `sm_75` host and an `sm_121` host taken through one read-only audit that
  produces two different diagnoses and two different repairs.
- **Status:** **drafted and validating** (`0 failures, 2 warnings`), already at
  `posts/nvidia-stack/architecture-aware-tensorrt-llm-cuda-onnx/`, not yet uploaded. See
  *Publication order*.
- **Search intent:** "no kernel image is available for execution on the device", "sm_120 is not
  compatible with the current PyTorch installation", "TORCH_CUDA_ARCH_LIST what to set"

### Part 7 — What Actually Changes Between GPU Generations

- **Slug:** what-changes-between-gpu-generations
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,000 · **Figures:** 13
- **Answers:** my kernel works on the old GPU and is slow or broken on the new one — what changed?
- **Assumes:** Part 6's account of compute capability and code images — the
  `#intuition-architecture-targets-are-executable-inventory` anchor.
- **Owns:** the porting-consequences story, explicitly **not** a spec table: the matrix-instruction
  lineage and the synchronization requirements it drops, TMA replacing hand-written global→shared
  copies, thread block clusters and distributed shared memory, tensor memory, the numeric formats
  each generation can execute rather than emulate, and the single most expensive misconception in
  the subject — that compute capability is a version number. It is an identifier with family
  semantics and no ordering: the scoping sweep confirmed against NVIDIA's own compute-capability
  listing that **four mutually incompatible targets ship under the Blackwell brand**, and that a
  numerically higher capability can lack a feature a lower one has. The generation after Blackwell
  is in the Toolkit already and belongs in this part; the part must be written so that adding the
  next row does not invalidate the argument.
- **Hands off:** which format to quantize to, to Part 10; how to write the kernel, to Part 9.
- **Worked example:** one tiled GEMM inner loop shown three times across three generations — the
  same arithmetic, three different data-movement and synchronization idioms, with the lines that
  had to change highlighted.
- **Key sources:** the per-architecture tuning guides in the CUDA Toolkit docs; PTX ISA release
  notes; the published Blackwell and Hopper microbenchmarking papers.
- **Search intent:** "Hopper vs Blackwell difference for developers", "thread block clusters
  distributed shared memory", "TMA tensor memory accelerator how to use", "sm_100 vs sm_120"
- **Note:** the sweep found the buying audience ("which GPU should I purchase") is unwinnable and
  fully owned by spec-table SEO. This part is written for the porting audience only, and the
  title must not promise a comparison table.

### Part 8 — The Memory Hierarchy After TMA

- **Slug:** gpu-memory-hierarchy-after-tma
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 7,500 · **Figures:** 12
- **Answers:** the classic coalescing-and-bank-conflicts advice is a decade old — what of it still
  holds?
- **Assumes:** Part 7's generation differences.
- **Owns:** coalescing, the shared-memory bank model, and the padding trick — then the modern
  correction: async copy, TMA, swizzled layouts, and the cases where padding is now the wrong
  answer. Register pressure and why maximising occupancy is a statistic, not a goal.
- **Hands off:** the language you write it in, to Part 9.
- **Worked example:** one transpose kernel measured in four layouts on the same GPU — naive,
  padded, swizzled, and TMA — with achieved bandwidth against a measured roofline for each.
- **Key sources:** the CUDA C++ Best Practices Guide (as the thing being updated, not restated);
  per-architecture tuning guides; CUTLASS layout and swizzle documentation.
- **Search intent:** "shared memory bank conflict padding", "memory coalescing CUDA explained",
  "cp.async vs TMA", "why is my CUDA kernel memory bound"
- **Note:** the sweep judged this topic thin unless narrowed — Lei Mao, siboehm and the Best
  Practices Guide own the classic form. The defensible angle is exactly the correction, so the
  post must lead with what is now out of date.

### Part 9 — One Kernel, Four Ways

- **Slug:** one-kernel-four-ways
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,000 · **Figures:** 12
- **Answers:** I need one fused kernel, not a career in HPC — what do I write it in?
- **Assumes:** Part 8's memory hierarchy.
- **Owns:** the same non-trivial fused kernel implemented in CUDA C++, Triton, the CuTe DSL and
  the tile-based Python path, on one GPU, reported on three axes: lines of code, time to working,
  and achieved bandwidth against a measured roofline. Includes the honest finding wherever the
  measurement contradicts the marketing.
- **Hands off:** nothing; this is a terminal spoke.
- **Worked example:** the four implementations themselves, published in full in the lab.
- **Key sources:** the Triton language documentation; CUTLASS and CuTe DSL documentation and
  examples; the CUDA Tile programming material; independent kernel benchmarks.
- **Search intent:** "Triton vs CUDA which should I learn", "CUTLASS CuTe DSL tutorial", "how to
  write a fused kernel for pytorch", "is Triton fast enough compared to CUDA"
- **Note:** not a SAXPY. A vector-add comparison proves nothing and every existing post uses one.

### Part 10 — What the Tensor Cores Actually Execute

- **Slug:** what-tensor-cores-actually-execute
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 7,500 · **Figures:** 12
- **Answers:** GGUF, GPTQ, AWQ, INT8, FP8, NVFP4 — which of these is arithmetic and which is just
  storage?
- **Assumes:** Part 7's per-generation numeric formats — the `#numeric-formats` anchor.
- **Owns:** the distinction almost nothing on the open web draws cleanly: weight-only
  quantization that dequantizes back to 16-bit and only saves memory, versus true low-precision
  math the tensor cores execute. Calibration, outlier handling, per-tensor vs per-channel vs
  per-block scaling, and where quality actually degrades.
- **Hands off:** serving throughput consequences to Part 12.
- **Worked example:** one linear layer's numbers followed through each scheme by hand — stored
  bits, the dequantization step if there is one, and the instruction that finally runs — then the
  measured memory and latency for each on one GPU.
- **Key sources:** the Model Optimizer documentation; the original GPTQ and AWQ papers; the
  OCP microscaling-format specification; per-architecture tuning guides for format support.
- **Search intent:** "FP8 vs INT8 quantization LLM", "GPTQ vs AWQ vs GGUF", "what is NVFP4",
  "does quantization hurt quality"
- **Note:** the sweep found this cluster is dominated by content farms recycling 2023-era claims
  that are now wrong. The correction is the reason the post exists.

### Part 11 — Sizing VRAM for LLM Serving

- **Slug:** sizing-vram-for-llm-serving
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,000 · **Figures:** 10
- **Answers:** how much VRAM does this model actually need at my concurrency, and why do the
  online calculators disagree with reality?
- **Assumes:** Part 6's KV-cache capacity math — the
  `#the-math-attention-shapes-and-kv-cache-capacity` anchor. **Does not re-derive it**; this part
  starts where that section stops.
- **Owns:** what the published calculators get wrong — the widely copied formula assumes
  multi-head attention and overstates GQA, MQA and MLA models, sometimes by an order of
  magnitude. Then paged KV blocks, why an engine preallocates and therefore reports zero free
  VRAM by design, activation and workspace terms nobody counts, and the concurrency cliff.
- **Hands off:** which engine to run it on, to Part 12.
- **Worked example:** three named models with genuinely different attention shapes sized by hand
  at four concurrency levels, then the same three measured, with the gap between prediction and
  measurement explained rather than hidden.
- **Key sources:** the attention papers for GQA, MQA and MLA; serving-engine documentation on
  memory fraction and block allocation; model configuration files as primary sources for shapes.
- **Search intent:** "how much VRAM do I need to run a 70B model", "KV cache size calculation",
  "gpu_memory_utilization", "why does vllm OOM at high concurrency"

### Part 12 — Choosing an Inference Engine

- **Slug:** choosing-an-inference-engine
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,000 · **Figures:** 10
- **Answers:** vLLM, TensorRT-LLM, SGLang or llama.cpp — and how would I know?
- **Assumes:** Part 11's memory model.
- **Owns:** the inversion. Instead of publishing one more leaderboard, teach the reader to
  characterise their own traffic — prefix reuse ratio, input:output token ratio, TTFT versus
  throughput SLO, model churn rate, how many distinct models per GPU — and show how each property
  moves the answer. Continuous batching, prefix caching and speculative decoding appear here as
  properties that interact with traffic, not as features.
- **Hands off:** NVIDIA's own product naming to Part 13.
- **Worked example:** one model, four traffic profiles, the same four engines, on identical
  hardware — with the ranking changing between profiles, which is the whole point.
- **Key sources:** each engine's own documentation; the independent serving-benchmark literature;
  the benchmarking harness's known client-side measurement limits.
- **Search intent:** "vLLM vs TensorRT-LLM", "SGLang vs vLLM benchmark", "fastest LLM inference
  engine", "is TensorRT-LLM worth the compile step"
- **Note:** every published benchmark in this space comes from a party with an interest in the
  answer, and several were produced with a client whose own overhead distorts the numbers. Any
  figure this post publishes carries the full reproducibility tuple or it is not published.

### Part 13 — Triton, Dynamo, NIM: NVIDIA's Serving Stack Disambiguated

- **Slug:** nvidia-serving-stack-disambiguated
- **Tier:** L2 · **Difficulty:** intermediate · **Est. words:** 4,500 · **Figures:** 8
- **Answers:** which of these is a server, which is a platform, which is a licensed container,
  and which one wraps which?
- **Assumes:** Part 12's engine landscape.
- **Owns:** the product map, stated in words NVIDIA's own pages will not use — what was renamed
  and when, what is a brand versus an artifact you install, where the open-source boundary sits,
  what the licensing implications are, and the cases where the answer is not to use any of them.
  Also the naming collision that costs people hours: NVIDIA's inference server and the unrelated
  kernel language share the name Triton.
- **Hands off:** nothing; terminal spoke.
- **Worked example:** one model served four ways, with the container image, the config surface and
  the licence for each laid side by side.
- **Key sources:** the rename announcements with dates; the respective repositories' licences;
  container registry tags as evidence of what is actually shipping.
- **Search intent:** "Triton inference server vs Dynamo", "what is NVIDIA NIM", "is NIM just vLLM
  in a container", "NVIDIA AI Enterprise licence"
- **Note:** a rename happened here and both names remain live in container tags and documentation,
  which is precisely why the post is needed. Every naming claim needs a dated primary source.

### Part 14 — Why Your Multi-GPU Job Hangs

- **Slug:** why-your-multi-gpu-job-hangs
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 7,500 · **Figures:** 12
- **Answers:** every rank sits at 0% and nothing has errored for six minutes — what do I do first?
- **Assumes:** Part 5's profiling workflow.
- **Owns:** a diagnostic procedure rather than a variable list. Confirming it is actually a
  collective and not a data-loader stall or a checkpoint write; collectives and why rank-order
  divergence presents as a hang rather than an error; reading an `NCCL_DEBUG=INFO` transcript to
  see which transport was actually selected; NVLink domains versus the network fabric; the
  startup deadlock class; and what the watchdog timeout is really telling you.
- **Hands off:** the parallelism decision that produced the collective, to Part 15.
- **Worked example:** one real hang transcript read line by line, ending at the specific rank and
  the specific mismatched call.
- **Key sources:** NCCL documentation and its troubleshooting section; the distributed watchdog
  implementation in the framework; published post-mortems of large-cluster stalls.
- **Search intent:** "NCCL timeout distributed training hang", "Watchdog caught collective
  operation timeout", "NCCL_DEBUG=INFO how to read", "multi GPU training hangs at start"
- **Note:** the sweep was explicit that listing environment variables with one-line descriptions
  is what every existing post does and that it teaches cargo cult. This post prints a procedure.

### Part 15 — The Parallelism Decision

- **Slug:** the-parallelism-decision
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,500 · **Figures:** 14
- **Answers:** data, tensor, pipeline, sequence, context, expert, sharded — in what order do I
  add them, and why?
- **Assumes:** Part 14's collectives and interconnect topology.
- **Owns:** each strategy's communication volume and which axis it shards; the ordering rule
  (start with pure data parallelism; keep the highest-volume strategy inside the fastest
  interconnect domain; add dimensions only when a real constraint forces it); sharded data
  parallelism versus tensor parallelism as different objects rather than alternatives;
  low-precision training and the frequently reproduced result that turning it on makes a job
  slower; distributed checkpointing and resharding; and failure recovery at scale.
- **Hands off:** nothing; terminal spoke.
- **Worked example:** one model sized so that it does not fit one GPU, placed four different ways
  across the same node count, with the communication volume computed for each and the measured
  step time next to the prediction.
- **Key sources:** the tensor, pipeline and sharded-parallelism papers; the framework's own
  performance-tuning guidance; the low-precision training recipe documentation and its issue
  tracker for the contradicting reports.
- **Search intent:** "tensor parallelism vs FSDP", "when to use pipeline parallelism", "FP8
  training slower than BF16", "how to choose parallelism strategy"

### Part 16 (optional) — Jetson's Version Lattice

- **Slug:** jetson-version-lattice
- **Tier:** L2 · **Difficulty:** intermediate · **Est. words:** 4,500 · **Figures:** 8
- **Answers:** which component pins which, and what does a mismatch look like before it announces
  itself?
- **Assumes:** Part 2's version model.
- **Owns:** the pinning graph across the board support package, the SDK, the inference runtime and
  the media stack; and the failure signatures that reveal a mismatch silently — an engine file
  rebuilt on every container start because the host and container runtimes differ by a patch
  version, encoder elements vanishing after a routine upgrade, several SDK versions installed
  simultaneously after an `apt upgrade`.
- **Hands off:** nothing; terminal spoke.
- **Worked example:** one board with a deliberately mismatched container, showing the silent
  rebuild in the logs and the time it costs per start.
- **Key sources:** the SDK and board-support-package release notes as the pinning source of
  truth; the vendor developer forum threads that document each signature.
- **Search intent:** "JetPack L4T version compatibility", "TensorRT version mismatch container
  Jetson", "DeepStream which JetPack"
- **Note:** smallest audience in the series, and the sweep says it is almost entirely unowned
  outside forum threads. Optional, and last — it is a domain spoke, not a rung.

## Publication order and cadence

Reading order is the numbering above and `series_position` follows it. Publication order does
not have to.

**Publish Parts 1, 2 and 3 first, in order.** They are the ladder; every spoke links back to one
of them, and a spoke published before its rung has nothing to link to.

**Part 6 is already drafted**, so it can ship immediately after Part 2 — the only part it names
as a prerequisite. It does not need Parts 3, 4 or 5. Shipping it fourth gets the series' highest
search-demand asset live early.

After that the spokes are independent and can ship in any order. Suggested by demand:
4 → 5 → 7 → 10 → 11 → 12 → 13 → 14 → 15 → 8 → 9 → 16.

Cadence: one part per week for the three ladder rungs, then one every one to two weeks for the
L4 spokes, which each carry a measured lab.

## Cross-links

Parts 1, 2 and 3 are the hubs. Every spoke names **at most one** prior part as a prerequisite and
links to its anchor rather than re-teaching it; a three-sentence recap is the maximum.

The dependency edges, all single:

```
1 → 2 → 3
2 → 6 → 7 → 8 → 9
2 → 16
3 → 4
3 → 5 → 14 → 15
6 → 11 → 12 → 13
7 → 10
```

No part links forward to an unpublished post. Forward links are added in the later part when it
ships, never by reopening the earlier one.

## The lab policy

This series has a hardware problem that the PostgreSQL series did not: **the authoring machine has
no NVIDIA GPU.** Every lab is therefore assigned to one of three tiers, and the tier is stated in
the part's own README so no reader is promised something they cannot run.

- **Tier A — no GPU required.** Compilation, inspection and arithmetic: `nvcc` targeting,
  fatbinary and PTX/SASS inspection with the object-dump tools, CMake target selection, ONNX
  graph inspection, and every memory-sizing calculation. These run in a CUDA development
  container on any x86 machine and are fully reproducible by the author and the reader.
  Parts 1, 2, 6, 11 and 16 can be built almost entirely on Tier A.
- **Tier B — one consumer GPU.** Anything that launches a kernel: occupancy, streams, the
  allocator and OOM reproductions, profiling, the transpose measurements, the four kernel
  implementations. Parts 3, 4, 5, 8, 9 and 10 need this. Captured on a rented single-GPU
  instance, with the full provenance line in the lab README.
- **Tier C — multi-GPU or datacenter.** Collectives, hangs, parallelism strategies, disaggregated
  serving, and any measurement that depends on a specific tensor-core generation. Parts 7, 12, 14
  and 15 need this. Rented by the hour, captured once, and published as recorded output with
  complete provenance.

**No invented numbers, at any tier.** Where a measurement cannot be made, the post publishes the
harness and the schema and says the number is not filled — the approach Part 6 already takes with
its benchmark report.

Prefer **one shared lab per thread** rather than one per post, following the PostgreSQL series:
the compatibility thread (2, 6, 16) shares one container and one audit script; the kernel thread
(7, 8, 9) shares one GPU instance and one measurement harness; the serving thread (11, 12, 13)
shares one model and one traffic generator.

## Open decisions for the user

1. **Category.** The existing member is `machine-learning`, and most readers will arrive from an
   ML search. But Parts 7, 8 and 9 are genuinely `computer-architecture`, and the house rule
   allows a new category once five posts would sit in it. Recommendation: put the whole series in
   `machine-learning` for consistent series navigation and because it matches the arrival path.
   The adjacent option is to split by part, which fragments the series index.
2. **Length.** Sixteen parts is large. Parts 1–6 are the defensible core — they alone deliver the
   compatibility and execution model and include the drafted pillar. Parts 7–15 are the spoke set
   and can be cut or deferred without breaking any dependency except the chains shown above.
   Part 16 is already marked optional.
3. **Part 9's four languages.** The fourth implementation targets a tile-based path that is newer
   than the other three and may not be stable enough to measure fairly at writing time. If the
   research sweep finds it is not, the post becomes *One Kernel, Three Ways* rather than waiting.

## What this series will not cover

Introductory CUDA — hello world, vector add, the threads/blocks/grids diagram — because NVIDIA's
own introduction plus the PMPP book own it completely. Reference material of any kind: API
signatures, parameter tables, the counter dictionary, the environment-variable list, the
compatibility matrix itself. GPU purchasing, SKU comparison and TFLOPS tables. Installation and
quickstart instructions for fast-moving stacks, which have the highest rot rate of anything
publishable. Graphics, ray tracing and the rendering pipeline. Omniverse, robotics simulation,
autonomous driving and the healthcare platforms — each is a separate domain with its own audience
and none of them is on the path from "capable engineer" to "fluent on this stack". Cloud
economics and instance pricing. And the competitive question of how this stack compares to other
vendors' — a legitimate topic, and a different series.
