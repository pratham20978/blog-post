# Source ledger — five-causes-of-cuda-out-of-memory

Series: nvidia-stack, part 4. Tier L3 — floors are 7 peer-reviewed or standard sources carrying an
identifier, and 4 distinct scholarly databases in the search log. Researched 2026-10-30, inline (no
agents).

Every PyTorch behaviour below was read in the source or the docs **at tag `v2.15.0`**
(raw.githubusercontent.com, saved to the session scratchpad), not recalled; line numbers refer to that
tag. NVIDIA and Linux pages were read live on 2026-10-30 and carry their version. Numbers the article
calls *measured* come from `lab/oom_lab.py` (capture `lab/captures.json`, 2026-10-30T11:44:17Z, NVIDIA
GB10, torch 2.15.0+cu132) and need no key; every published number, version, date, attribution and named
result carries one below.

**What the measurements are, and are not.** The lab ran on an NVIDIA GB10 (Dell Pro Max with GB10), an
integrated GPU whose 121.63 GiB are the operating system's memory. Exhausting it for real would exhaust
the machine, which had a desktop session open, so the lab emulates a 24 GiB card: PyTorch's
per-process memory fraction is reset before every phase to 24 GiB minus what NVML says other compute
processes and this process's non-PyTorch memory hold. The allocator, its splitting, its retries and its
message are real; the size of the card is not. Every message therefore carries an "allowed" clause and
the GB10's real total and free, and the article says so where the messages first appear.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T1 | Tang, Qiao, Yin, Liang, Shen, Yang, "Training large-scale language models with limited GPU memory: a survey" (abstract record only; full text not open) | Frontiers of Information Technology & Electronic Engineering | 2025 | 10.1631/fitee.2300710 | peer-reviewed | https://doi.org/10.1631/fitee.2300710 | 2026-10-30 |
| S2 | T1 | Wilson, Johnstone, Neely, Boles, "Dynamic Storage Allocation: A Survey and Critical Review" (read in the authors' UT Austin copy) | IWMM 1995, LNCS 986 | 1995 | 10.1007/3-540-60368-9_19 | peer-reviewed | https://www.cs.hmc.edu/~oneill/gc-library/Wilson-Alloc-Survey-1995.pdf | 2026-10-30 |
| S3 | T1 | Johnstone, Wilson, "The Memory Fragmentation Problem: Solved?" (read in a course copy) | ISMM 1998, pp. 26–36 | 1998 | 10.1145/286860.286864 | peer-reviewed | https://sfkaplan.people.amherst.edu/courses/2016/fall/COSC-461/documents/Johnstone-Memory-fragmentation-problem.pdf | 2026-10-30 |
| S4 | T1 | Paszke et al., "PyTorch: An Imperative Style, High-Performance Deep Learning Library" | NeurIPS 2019 | 2019 | arXiv:1912.01703 | peer-reviewed | https://arxiv.org/abs/1912.01703 | 2026-10-30 |
| S5 | T1 | Rajbhandari, Rasley, Ruwase, He, "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models" (read in arXiv:1910.02054) | SC20 | 2020 | 10.1109/SC41405.2020.00024 | peer-reviewed | https://arxiv.org/abs/1910.02054 | 2026-10-30 |
| S6 | T1 | Zhao et al., "PyTorch FSDP: Experiences on Scaling Fully Sharded Data Parallel" (read in arXiv:2304.11277) | PVLDB 16(12) | 2023 | 10.14778/3611540.3611569 | peer-reviewed | https://arxiv.org/abs/2304.11277 | 2026-10-30 |
| S7 | T1 | Guo et al., "GMLake: Efficient and Transparent GPU Memory Defragmentation for Large-scale DNN Training with Virtual Memory Stitching" (read in arXiv:2401.08156) | ASPLOS 2024 | 2024 | 10.1145/3620665.3640423 | peer-reviewed | https://arxiv.org/abs/2401.08156 | 2026-10-30 |
| S8 | T1 | Zhang, Xiao, Zhang, Liu, Lin, Yang, "An Empirical Study on Program Failures of Deep Learning Jobs" (author copy) | ICSE 2020 | 2020 | 10.1145/3377811.3380362 | peer-reviewed | https://hongyujohn.github.io/icse20-main-199.pdf | 2026-10-30 |
| S9 | T1 | Chen, Xu, Zhang, Guestrin, "Training Deep Nets with Sublinear Memory Cost" (no venue in OpenAlex; DBLP blocked) | arXiv | 2016 | arXiv:1604.06174 | preprint | https://arxiv.org/abs/1604.06174 | 2026-10-30 |
| S10 | T2 | PyTorch docs, "CUDA semantics", sections Memory management, Optimizing memory usage with PYTORCH_ALLOC_CONF, cuBLAS workspaces (docs/source/notes/cuda.md at v2.15.0) | — | 2026 | — | official-docs | https://docs.pytorch.org/docs/stable/notes/cuda.html | 2026-10-30 |
| S11 | T2 | PyTorch docs, "Understanding CUDA Memory Usage" (docs/source/torch_cuda_memory.md at v2.15.0) | — | 2026 | — | official-docs | https://docs.pytorch.org/docs/stable/torch_cuda_memory.html | 2026-10-30 |
| S12 | T2 | PyTorch docs, "Frequently Asked Questions" (docs/source/notes/faq.md at v2.15.0) | — | 2026 | — | official-docs | https://docs.pytorch.org/docs/stable/notes/faq.html | 2026-10-30 |
| S13 | T3 | PyTorch source, c10/cuda/CUDACachingAllocator.cpp at v2.15.0 | — | 2026 | tag v2.15.0 | source | https://github.com/pytorch/pytorch/blob/v2.15.0/c10/cuda/CUDACachingAllocator.cpp | 2026-10-30 |
| S14 | T3 | PyTorch source, c10/core/AllocatorConfig.h and .cpp, c10/cuda/CUDAAllocatorConfig.h at v2.15.0 | — | 2026 | tag v2.15.0 | source | https://github.com/pytorch/pytorch/blob/v2.15.0/c10/core/AllocatorConfig.h | 2026-10-30 |
| S15 | T3 | PyTorch source, aten/src/ATen/cuda/CublasHandlePool.cpp at v2.15.0 | — | 2026 | tag v2.15.0 | source | https://github.com/pytorch/pytorch/blob/v2.15.0/aten/src/ATen/cuda/CublasHandlePool.cpp | 2026-10-30 |
| S16 | T3 | PyTorch source, torch/cuda/__init__.py (device_memory_used) and torch/cuda/memory.py (set_per_process_memory_fraction) at v2.15.0 | — | 2026 | tag v2.15.0 | source | https://github.com/pytorch/pytorch/blob/v2.15.0/torch/cuda/__init__.py | 2026-10-30 |
| S17 | T3 | PyTorch pull requests #96995 (expandable blocks), #99093 and #130959 (enable by default), #113481 (do not recommend max_split_size_mb first), read through the GitHub REST API | — | 2023–2024 | PRs 96995, 99093, 113481, 130959 | source | https://github.com/pytorch/pytorch/pull/113481 | 2026-10-30 |
| S18 | T2 | Edward Yang, "When does fragmentation occur in the CUDA caching allocator?" (PyTorch devlog; the post says it was drafted by Claude and edited by the author) | PyTorch devlogs | 2026 | — | official-docs | https://docs.pytorch.org/devlogs/eager/2026-06-01-cuda-caching-allocator/ | 2026-10-30 |
| S19 | T2 | NVIDIA, CUDA Programming Guide v13.4.2, §4.7 Lazy Loading | — | 2026 | — | official-docs | https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/lazy-loading.html | 2026-10-30 |
| S20 | T2 | NVIDIA, CUDA Driver API v13.4, Virtual Memory Management | — | 2026 | — | official-docs | https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__VA.html | 2026-10-30 |
| S21 | T2 | NVIDIA cuda-python docs, NVML nvmlDeviceGetComputeRunningProcesses_v3 (the NVML reference page it mirrors now returns 404) | — | 2026 | — | official-docs | https://nvidia.github.io/cuda-python/cuda-bindings/latest/module/generated/cuda.bindings.nvml.device_get_compute_running_processes_v3.html | 2026-10-30 |
| S22 | T2 | NVIDIA, DGX Spark User Guide, Known Issues (last updated 2026-10-21) | — | 2026 | — | official-docs | https://docs.nvidia.com/dgx/dgx-spark/known-issues.html | 2026-10-30 |
| S23 | T2 | Linux man-pages 6.18, _exit(2) | — | 2026 | — | official-docs | https://man7.org/linux/man-pages/man2/_exit.2.html | 2026-10-30 |
| S24 | T2 | Linux man-pages 6.19, wait(2) | — | 2026 | — | official-docs | https://man7.org/linux/man-pages/man2/wait.2.html | 2026-10-30 |
| S25 | T3 | PyPI, torch release metadata (JSON API) | — | 2026 | torch 2.15.0 | source | https://pypi.org/pypi/torch/json | 2026-10-30 |
| S26 | T2 | PyTorch docs, "torch.optim", section Algorithms and implementation defaults (docs/source/optim.md at v2.15.0) | — | 2026 | — | official-docs | https://docs.pytorch.org/docs/stable/optim.html | 2026-10-30 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | OpenAlex | full-text search "GPU memory management deep learning training survey", sorted by citations | noise: the PyTorch 2019 paper first, then unrelated surveys; switched to title searches |
| 2 | 1 | OpenAlex | full-text search "GPU memory fragmentation deep learning training" | noise again; confirmed PyTorch 2019 (W2970971581) as the most-cited system paper in the area |
| 3 | 1 | Semantic Scholar | paper search "GPU memory fragmentation deep neural network training allocator" | HTTP 429 for the session; blocked, not retried |
| 4 | 1 | arXiv | all: "GPU memory fragmentation caching allocator" | GMLake (2401.08156) and an unrelated 2026 theory preprint on allocation bounds |
| 5 | 1 | Google Scholar | "survey GPU memory optimization deep learning training" | Tang et al. 2025 (FITEE), the memory-specific survey used as the map; Zhang et al. 2019, an arXiv overview |
| 6 | 1 | OpenAlex | title.search "dynamic storage allocation survey critical review", and two phrasings of a GPU-memory survey title | Wilson et al. 1995 (602 citations), the allocator survey; the GPU-memory phrasings returned 0 |
| 7 | 1 | Crossref | bibliographic query for seven central titles | DOIs for Tang 2025, Zhang 2020, Gao 2020 (DNNMem), ZeRO, FSDP, GMLake, Johnstone & Wilson 1998 |
| 8 | 1 | OpenAlex | works/doi lookups for the eight DOIs | open copies on arXiv for ZeRO, FSDP and GMLake; none for Zhang 2020, Tang 2025, Wilson 1995, Johnstone 1998 |
| 9 | 1 | Google Scholar | the four closed titles, for author PDFs | citation-only records; no PDFs |
| 10 | 1 | Web search | author copies of Zhang 2020, Gao 2020, Wilson 1995, Johnstone 1998 | Zhang's author copy, the UT Austin copy of Wilson, an Amherst course copy of Johnstone; Gao (DNNMem) only behind a Microsoft page that returned 403, so it is not cited |
| 11 | 1 | OpenAlex | forward chase: filter cites:W4394998892 (GMLake) | 30 citing works; MOVie (IJCNN 2025) reports the same split-merge fragmentation under memory optimisations (abstract only, not cited); vAttention (serving, Part 11's ground); a PyTorch data-path bug study about contiguity, not used |
| 12 | 1 | OpenAlex | forward chase: cites:W2970971581 (PyTorch 2019) with title.search fragmentation, allocator, out of memory | 2, 1 and 0 hits, none about GPU allocation; the forward literature on the allocator runs through GMLake and FSDP instead |
| 13 | 1 | arXiv | full texts of 1912.01703, 1910.02054, 2304.11277, 2401.08156, 1604.06174 | backward chase: PyTorch §5.3 builds on CPU allocators (refs 39–41: Hoard, jemalloc, tcmalloc); GMLake's allocator is BFC (its ref 76) and its fragmentation cause is recomputation, offloading and LoRA |
| 14 | 1 | DBLP | "Training Deep Nets with Sublinear Memory Cost" | bot wall (non-JSON); OpenAlex lists it as arXiv only, so the post labels it a preprint |
| 15 | 2 | PyTorch v2.15.0 source | CUDACachingAllocator.cpp, AllocatorConfig.*, CUDAAllocatorConfig.h, CublasHandlePool.cpp, torch/cuda/*.py, docs/*.md | the constants, the malloc retry chain, the message format, the NVML process report, expandable segments, env-variable order, the cuBLAS workspace |
| 16 | 2 | NVIDIA docs | CUDA lazy loading; Driver API virtual memory management; NVML compute processes | 12.2 default on Linux, EAGER; cuMemCreate and cuMemMap semantics; graphics processes are not listed |
| 17 | 4 | GitHub REST API | pytorch/pytorch PRs with "expandable segments" by zdevito; title search 2023 | #96995 (2023-03-17), #99093 and #130959 (enable by default), #113481 (max_split_size_mb no longer first advice) |
| 18 | 4 | PyTorch docs | devlog on caching-allocator fragmentation; FAQ on accumulating history | the devlog's page-size key `expandable_segments_page_size` is not parsed at v2.15.0 (open question); the FAQ's training-loop example, which the lab measured |
| 19 | 4 | NVIDIA docs | DGX Spark known issues | nvidia-smi memory "Not Supported" on iGPUs; cudaMemGetInfo misses reclaimable memory under unified memory |
| 20 | 5 | Linux man-pages | _exit(2), wait(2) | file descriptors closed at termination; zombie keeps PID, status and usage only; orphans adopted by init or a subreaper |
| 21 | 3 | PyPI | torch JSON metadata | torch 2.15.0 is the newest release on 2026-10-30; its Linux wheel requires cuda-toolkit 13.2.2, NCCL 2.30.7, cuDNN 9.26 |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | Over three weeks in October 2018, 434 of 4,960 failed jobs on Microsoft's Philly platform were GPU out-of-memory failures, 8.8% of the total and the largest deep-learning-specific category (65.0% of it) | S8 §3, §4.1, Table 1 | failures caused by code or script defects; one platform; 2018 |
| L02 | In the study's 400-failure sample, most of its 39 GPU out-of-memory failures came from an overlarge batch size or an overcomplicated model | S8 §5.2.1, Finding 6 | manual root-cause analysis of the sample |
| L03 | The survey divides training memory into model parameters, model states and activations | S1 abstract | abstract only |
| L04 | On a GPU, cudaFree may block its caller until all previously queued work on all GPUs completes; PyTorch's allocator avoids it by building a cache incrementally and reusing it | S4 §5.3 | design rationale, 2019 |
| L05 | PyTorch's allocator rounds allocations up to multiples of 512 bytes and keeps a separate pool per CUDA stream; because the CPU runs ahead, memory freed on the CPU can be reused at once on the same stream | S4 §5.3 | 2019 description; the rounding is still 512 bytes at v2.15.0 (L14) |
| L06 | Allocating incrementally rather than all GPU memory at start-up lets other GPU-using Python packages run in the same process | S4 §5.3 | — |
| L07 | Fragmentation is the inability to reuse memory that is free; external fragmentation is free blocks too small for the sizes requested; fragmentation is caused by isolated deaths, free areas whose neighbours are still in use | S2 §2.1, §2.3 | general allocator theory |
| L08 | For eight real C and C++ programs, best fit and address-ordered first fit averaged under 1% fragmentation; the authors note unusual program behaviours may be missing from their sample | S3 abstract, §5 | 1998 traces of CPU programs |
| L09 | ZeRO's authors observed significant fragmentation training very large models, with out-of-memory errors while over 30% of memory was still available in extreme cases, and trace it to interleaving short-lived and long-lived tensors | S5 §3.2, §4.2.3 | very large models; the extreme cases |
| L10 | GMLake reports up to 30% fragmentation under the caching allocator (a best-fit-with-coalescing pool) when memory-reduction techniques are used, and that stitching virtual memory cut usage by 9.2 GB on average (up to 25 GB) and fragmentation by 15% (up to 33%) across eight LLMs on an 80 GB A100 | S7 abstract, §1 | the authors' evaluation against PyTorch's allocator |
| L11 | The caching allocator keeps blocks per stream; over-allocation to one stream can make it fail to serve another and force a blocking sequence of cudaFree calls (a cudaMalloc retry) that degrades throughput; num_alloc_retries in memory_stats() is the indicator | S6 §3.4.1, §5 | FSDP's multi-stream setting |
| L12 | Recomputing activations during the backward pass trades extra computation for memory (activation checkpointing) | S9 abstract, §1 | preprint |
| L13 | At v2.15.0: every size is rounded to at least 512 bytes; requests up to 1 MiB come from 2 MiB small-pool segments; requests between 1 and 10 MiB get a 20 MiB segment (`large_segment_size_mb`, default 20); larger requests are rounded up to 2 MiB | S14 AllocatorConfig.h lines 14–23 and 338; S13 get_allocation_size | v2.15.0 |
| L14 | The allocator picks the smallest cached block that fits and may split it; when cudaMalloc fails it frees enough large cached blocks and retries (only when max_split_size_mb is set: release_available_cached_blocks returns at once otherwise), then synchronizes, frees all unsplit cached blocks and retries | S13 design comment, lines 106–124; malloc(); release_available_cached_blocks() | v2.15.0; the design comment omits the max_split_size_mb condition |
| L15 | By the time the out-of-memory error is raised, the allocator has already returned every releasable cached block; what remains reserved but unallocated is split from blocks partly in use | S13 comment in malloc(), before the error | v2.15.0; release is skipped during CUDA graph capture |
| L16 | The message's total and free come from cudaMemGetInfo; its per-process lines come from NVML's compute-process list; the "allowed" clause appears only when a memory fraction is set; it then gives allocated by PyTorch, private pools and reserved but unallocated | S13 malloc() and reportProcessMemoryInfo() | v2.15.0 message format |
| L17 | The per-process lines are left out when NVML's process query fails, which the source says to expect on platforms with partial NVML support such as Tegra and Jetson | S13 reportProcessMemoryInfo() | v2.15.0 |
| L18 | Expandable segments reserve virtual address space of 1 1/8 of device memory per segment, one segment per stream, and map physical memory on demand with cuMemCreate and cuMemMap, in 2 MiB pages for the small pool and 20 MiB (`large_segment_size`) pages for the large pool | S13 Note [Expandable Segments], growableReserveBytes, get segment size | v2.15.0 |
| L19 | Expandable segments cannot share memory over CUDA IPC and do not work with cudaDeviceEnablePeerAccess-style sharing without the allocator's own mapping | S13 Note [Expandable Segments], Limitations | v2.15.0 |
| L20 | Expandable segments still fragment when live blocks pin splits, for instance long-lived allocations interleaved with short-lived ones in the same pool | S18 | devlog, 2026-06-01 |
| L21 | At v2.15.0 expandable_segments defaults to false, and the docs call it experimental | S14 AllocatorConfig.h line 351; S10 | v2.15.0 |
| L22 | Expandable segments arrived in PR #96995 (opened 2023-03-17); turning them on by default was proposed in #99093 (2023-04-13) and #130959 (opened 2024-07-17, closed 2024-11-06) | S17 | PR metadata; merge state is not reliable for ghstack PRs, so the post claims only the proposals |
| L23 | PR #113481 (November 2023) stopped recommending max_split_size_mb first: set as a fragmentation workaround, it caused later problems such as degraded performance from freeing empty segments, and expandable segments are less likely to need synchronous GPU operations | S17 | PR description |
| L24 | The docs present PYTORCH_ALLOC_CONF as the variable and PYTORCH_CUDA_ALLOC_CONF as an alias kept for backward compatibility, while the parser reads PYTORCH_CUDA_ALLOC_CONF first and uses only the first one set | S10; S14 AllocatorConfig.cpp lines 40–60, CUDAAllocatorConfig.h lines 214–235 | v2.15.0; the lab measured the outcome |
| L25 | max_split_size_mb stops the allocator splitting blocks larger than the given size; the docs call it a last resort for workloads failing with many inactive split blocks, with a performance cost from zero to substantial, and it is ignored under backend:cudaMallocAsync | S10 | v2.15.0 docs |
| L26 | Cached memory shows as used in nvidia-smi; empty_cache() releases unused cached memory for other GPU applications but cannot increase the memory available to PyTorch for tensors in use | S10 Memory management | v2.15.0 docs |
| L27 | Memory snapshots are recorded with torch.cuda.memory._record_memory_history() and _dump_snapshot() and opened in pytorch.org/memory_viz; they see only memory from PyTorch's allocator, not memory from raw CUDA calls, cuda-python or NCCL | S11 | v2.15.0 docs |
| L28 | The docs suggest comparing torch.cuda.device_memory_used(), NVML's device-wide used memory read through pynvml, with PyTorch's own numbers to find non-PyTorch allocations | S11; S16 device_memory_used() | needs nvidia-ml-py, which torch does not install |
| L29 | torch.cuda.set_per_process_memory_fraction limits the caching allocator to the fraction times the device's total memory and raises out-of-memory beyond it | S16 memory.py docstring; S13 alloc_block() | v2.15.0 |
| L30 | At v2.15.0 ATen allocates a cuBLAS workspace for each operation from the caching allocator and releases it when the operation returns, unless TORCH_CUBLAS_WORKSPACE_CACHE=1; the default size is 32 MiB on compute capability 9.x to 12.x | S10 cuBLAS workspaces; S15 parseChosenWorkspaceSize() | v2.15.0; changed from earlier releases, which cached one per handle and stream |
| L31 | The FAQ's first advice for out-of-memory is not to accumulate history across the training loop: total_loss += loss keeps autograd history, fixed with float(loss) | S12 | v2.15.0 docs |
| L32 | Lazy loading arrived in CUDA 11.7 and became the default on Linux in 12.2 (all platforms in 12.3); it defers loading modules, and allocating their memory, until they are needed; CUDA_MODULE_LOADING=EAGER turns it off; it needs driver 515 or newer | S19 | CUDA 13.4.2 guide |
| L33 | An application that takes all memory at start-up can later fail to allocate memory for lazily loaded modules | S19 | — |
| L34 | NVML's running-process query for compute returns only processes with a compute context; graphics applications are not listed; its used-memory field is all memory the application uses | S21 | NVML via cuda-python docs |
| L35 | cuMemCreate makes a physical allocation with no mapping; cuMemAddressReserve reserves virtual addresses without backing; cuMemMap maps one onto the other; cuMemUnmap and cuMemRelease undo them | S20 | CUDA 13.4 |
| L36 | On iGPU platforms such as DGX Spark, nvidia-smi reports Memory-Usage as Not Supported, by design, because there is no dedicated framebuffer, while per-process memory is still listed | S22 | page updated 2026-10-21 |
| L37 | Under unified memory, cudaMemGetInfo does not count memory the operating system could reclaim and may report less than can be allocated; NVIDIA advises not relying on it alone and reading /proc/meminfo | S22 | DGX Spark guidance |
| L38 | When a process terminates the kernel closes all its file descriptors; its children are adopted by init or the nearest subreaper | S23 | Linux man-pages 6.18 |
| L39 | A zombie is a child that has terminated but has not been waited for; the kernel keeps only its PID, termination status and resource usage until it is reaped | S24 | Linux man-pages 6.19 |
| L40 | torch 2.15.0 is the newest torch on PyPI on 2026-10-30, and its Linux wheel depends on cuda-toolkit 13.2.2, NCCL 2.30.7 and cuDNN 9.26 | S25 | read 2026-10-30 |
| L41 | Adam's default implementation is foreach, which combines the parameters into a multi-tensor and runs each step of the update on all of them at once, when all tensors are native and on a supported device | S26 Algorithms, implementation table | v2.15.0 docs |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S7 | Figure 1 | splitting versus stitching / L10 | shows a split pool next to a stitched one | arXiv non-exclusive licence; no reuse licence | https://arxiv.org/abs/2401.08156 | do not reuse: the article draws the slivers its own run produced, from the snapshot |
| F2 | S18 | segment printouts | expandable segments / L20 | text dumps, not figures | — | https://docs.pytorch.org/devlogs/eager/2026-06-01-cuda-caching-allocator/ | do not reuse: nothing to reuse |

## Literature and disagreement

- **Fragmentation was "solved", and is not, here.** Johnstone and Wilson found best fit nearly
  fragmentation-free on CPU programs (L08); PyTorch's allocator is best fit (L14), yet ZeRO (L09) and
  GMLake (L10) report a third of memory lost to it in deep-learning training. The 1998 paper itself says
  unusual allocation behaviour could be missing from its sample. The lab shows why: tensors of 256 MiB
  and 384 MiB with interleaved lifetimes leave 128 MiB tails pinned by live state.
- **Which variable configures the allocator.** The docs call PYTORCH_CUDA_ALLOC_CONF an alias of
  PYTORCH_ALLOC_CONF; the code reads the alias first and the lab measured that it wins when both are
  set (L24). The out-of-memory message itself still says PYTORCH_CUDA_ALLOC_CONF.
- **The FAQ's example and the GPU.** The FAQ's `total_loss += loss` keeps history (L31); the lab
  measured that in a training loop it adds no GPU memory per step, because backward() already freed what
  each step saved, while the same habit in an evaluation loop held 1.55 GiB per batch.
- **Default or not.** Expandable segments were twice proposed as the default (L22) and are still off
  and called experimental in 2.15.0 (L21).

## Open questions

- The June 2026 devlog names `expandable_segments_page_size` as the large-page setting; v2.15.0 parses
  no such key and sizes the page from `large_segment_size_mb` (L18). The post describes v2.15.0 only.
- What the 548 MiB NCCL allocated for a single rank consists of (buffers, kernels, proxy state) is not
  documented; the post reports the measured total and what destroy_process_group() returned, no
  breakdown.
- Whether a GB10's cudaMemGetInfo free tracks MemFree on every driver release: measured equal to
  0.01 GiB on driver 595.71.05 only.
- The CUDA context sizes are this GB10's, with lazy and eager loading; discrete cards differ and no
  primary source gives typical sizes, so the post quotes only its own measurement.
