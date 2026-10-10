# Source ledger — gpu-idle-at-100-percent-utilization

Series: nvidia-stack, part 3. Tier L3 — floors are 7 peer-reviewed or standard sources carrying an
identifier, and 4 distinct scholarly databases in the search log.

Every NVIDIA and PyTorch definition, number and version below was read out of the primary page or
the source file at a release tag on **2026-09-24**, not recalled. Pages were saved to the session
scratchpad and each load-bearing sentence was re-read in the saved text before it went into the
Claims table. Where a value can move — a documentation page, a release — the Condition column says
so and names the date it was read.

**What this post rests on that is not a measurement.** The worked example's durations are model
inputs (round numbers chosen to be followed by hand), computed by `lab/queue_model.py`. They carry
no ledger key because they are not claims about the world; the article labels them as a model in the
prose and in every caption that draws them. The machine that wrote this has no NVIDIA GPU; the
Tier B lab measures the real values and its results file ships empty.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S01 | T1 | Ye, Gao, Hu, Sun, Wang, Luo, Zhang, Wen, "Deep Learning Workload Scheduling in GPU Datacenters: A Survey" | ACM Computing Surveys 56(6) | 2024 | 10.1145/3638757 | peer-reviewed | https://doi.org/10.1145/3638757 | 2026-09-24 |
| S02 | T1 | Paszke et al., "PyTorch: An Imperative Style, High-Performance Deep Learning Library" | NeurIPS 2019 | 2019 | arXiv:1912.01703v1 | peer-reviewed | https://proceedings.neurips.cc/paper/2019/hash/bdbca288fee7f92f2bfa9f7012727740-Abstract.html | 2026-09-24 |
| S03 | T1 | Ansel et al., "PyTorch 2: Faster Machine Learning Through Dynamic Python Bytecode Transformation and Graph Compilation" | ASPLOS '24 | 2024 | 10.1145/3620665.3640366 | peer-reviewed | https://doi.org/10.1145/3620665.3640366 | 2026-09-24 |
| S04 | T1 | Kwon, Yu, Jeong, Chun, "Nimble: Lightweight and Parallel GPU Task Scheduling for Deep Learning" | NeurIPS 2020 | 2020 | arXiv:2012.02732v1 | peer-reviewed | https://proceedings.neurips.cc/paper/2020/hash/5f0ad4db43d8723d18169b2e4817a160-Abstract.html | 2026-09-24 |
| S05 | T1 | Gao et al., "An Empirical Study on Low GPU Utilization of Deep Learning Jobs" | IEEE/ACM ICSE 2024 | 2024 | 10.1145/3597503.3639232 | peer-reviewed | https://www.microsoft.com/en-us/research/wp-content/uploads/2024/01/gpu-util-icse2024.pdf | 2026-09-24 |
| S06 | T1 | Jeon et al., "Analysis of Large-Scale Multi-Tenant GPU Clusters for DNN Training Workloads" | USENIX ATC '19 | 2019 | ISBN 978-1-939133-03-8 | peer-reviewed | https://www.usenix.org/system/files/atc19-jeon.pdf | 2026-09-24 |
| S07 | T1 | Gleeson, Krishnan, Gabel, Janapa Reddi, de Lara, Pekhimenko, "RL-Scope: Cross-Stack Profiling for Deep Reinforcement Learning Workloads" | MLSys 2021 | 2021 | arXiv:2102.04285v2 | peer-reviewed | https://arxiv.org/abs/2102.04285v2 | 2026-09-24 |
| S08 | T1 | Elvinger et al., "Understanding GPU Resource Interference One Level Deeper" | ACM SoCC 2025 | 2025 | 10.1145/3772052.3772270 | peer-reviewed | https://arxiv.org/abs/2501.16909 | 2026-09-24 |
| S09 | T1 | Weng et al., "MLaaS in the Wild: Workload Analysis and Scheduling in Large-Scale Heterogeneous GPU Clusters" | USENIX NSDI '22 | 2022 | ISBN 978-1-939133-27-4 | peer-reviewed | https://www.usenix.org/system/files/nsdi22-paper-weng.pdf | 2026-09-24 |
| S10 | T1 | Zheng et al., "Grape: Practical and Efficient Graph-based Executions for Dynamic Deep Neural Networks on GPUs" | IEEE/ACM MICRO 2023 | 2023 | 10.1145/3613424.3614248 | peer-reviewed | https://doi.org/10.1145/3613424.3614248 | 2026-09-24 |
| S11 | T1 | Ghosh, Nayak, Panwar, Basu, "GraCE: Unlocking CUDA Graphs with Compiler Support for ML Workloads" (published version of the PyGraph preprint, arXiv:2503.19779) | USENIX OSDI '26 | 2026 | ISBN 978-1-939133-55-7 | peer-reviewed | https://www.usenix.org/system/files/osdi26-ghosh.pdf | 2026-09-24 |
| S12 | T1 | Ekelund, Markidis, Peng, "Boosting Performance of Iterative Applications on GPUs: Kernel Batching with CUDA Graphs" | Euromicro PDP 2025 | 2025 | 10.1109/PDP66500.2025.00019 | peer-reviewed | https://arxiv.org/abs/2501.09398v1 | 2026-09-24 |
| S13 | T1 | Mohan, Phanishayee, Raniwala, Chidambaram, "Analyzing and Mitigating Data Stalls in DNN Training" | PVLDB 14(5) | 2021 | 10.14778/3446095.3446100 | peer-reviewed | https://arxiv.org/abs/2007.06775v3 | 2026-09-24 |
| S14 | T1 | Yeung, Borowiec, Friday, Harper, Garraghan, "Towards GPU Utilization Prediction for Cloud Deep Learning" | USENIX HotCloud '20 | 2020 | USENIX HotCloud '20 paper (no DOI registered) | peer-reviewed | https://www.usenix.org/system/files/hotcloud20_paper_yeung.pdf | 2026-09-24 |
| S15 | T2 | NVIDIA, System Management Interface (`nvidia-smi`) documentation, *Utilization* field descriptions | NVIDIA docs | 2026 | — | official-docs | https://docs.nvidia.com/deploy/nvidia-smi/index.html | 2026-09-24 |
| S16 | T2 | NVIDIA, NVML API Reference — `nvmlUtilization_t` and `nvmlDeviceGetUtilizationRates` | NVIDIA docs | 2026 | — | official-docs | https://docs.nvidia.com/deploy/nvml-api/latest/api/structnvmlUtilization__t.html | 2026-09-24 |
| S17 | T2 | NVIDIA, DCGM User Guide — *Feature Overview*, Profiling Metrics | NVIDIA docs | 2026 | — | official-docs | https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html | 2026-09-24 |
| S18 | T2 | NVIDIA, DCGM Changelog (4.6.0 and 4.7.0 entries) | NVIDIA docs | 2026 | — | official-docs | https://docs.nvidia.com/datacenter/dcgm/latest/release-notes/changelog.html | 2026-09-24 |
| S19 | T2 | NVIDIA, Nsight Systems User Guide v2026.5 — *GPU Metrics*, *CUDA Trace* | NVIDIA docs | 2026 | — | official-docs | https://docs.nvidia.com/nsight-systems/UserGuide/index.html | 2026-09-24 |
| S20 | T2 | NVIDIA, CUDA Programming Guide v13.4.2 — §2.1, §2.5 *Asynchronous Execution*, §3.1.3 *More on Streams and Events* | NVIDIA docs | 2026 | — | official-docs | https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/asynchronous-execution.html | 2026-09-24 |
| S21 | T2 | NVIDIA, CUDA Programming Guide v13.4.2 — §4.2 *CUDA Graphs* | NVIDIA docs | 2026 | — | official-docs | https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/cuda-graphs.html | 2026-09-24 |
| S22 | T2 | NVIDIA, CUDA Programming Guide v13.4.2 — §5.2 *CUDA Environment Variables* | NVIDIA docs | 2026 | — | official-docs | https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/environment-variables.html | 2026-09-24 |
| S23 | T2 | NVIDIA, CUDA Runtime API 13.4 — Event Management, Stream Management, Device Management | NVIDIA docs | 2026 | — | official-docs | https://docs.nvidia.com/cuda/cuda-runtime-api/cuda_runtime_api/group__CUDART__EVENT.html | 2026-09-24 |
| S24 | T2 | NVIDIA, CUDA Runtime API 13.4 — §2 *API synchronization behavior*, §3 *Stream synchronization behavior* | NVIDIA docs | 2026 | — | official-docs | https://docs.nvidia.com/cuda/cuda-runtime-api/api-sync-behavior.html | 2026-09-24 |
| S25 | T2 | NVIDIA, CUDA Toolkit 13.4 Update 1 Release Notes; archived 12.0, 12.3 guide and 12.8 release notes | NVIDIA docs | 2026 | — | official-docs | https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html | 2026-09-24 |
| S26 | T3 | Gray (NVIDIA), "Getting Started with CUDA Graphs" — measured experiment with full code listing | NVIDIA Technical Blog | 2019 | — | source | https://developer.nvidia.com/blog/cuda-graphs/ | 2026-09-24 |
| S27 | T3 | Hoffman, Oh (NVIDIA), "Constant Time Launch for Straight-Line CUDA Graphs and Other Performance Enhancements" | NVIDIA Technical Blog | 2024 | — | source | https://developer.nvidia.com/blog/constant-time-launch-for-straight-line-cuda-graphs-and-other-performance-enhancements/ | 2026-09-24 |
| S28 | T3 | Nguyen, Carilli, Eryilmaz, Singh, Lin, Gimelshein, Desmaison, Yang (PyTorch and NVIDIA), "Accelerating PyTorch with CUDA Graphs" | PyTorch Blog | 2021 | — | source | https://pytorch.org/blog/accelerating-pytorch-with-cuda-graphs/ | 2026-09-24 |
| S29 | T2 | PyTorch 2.14 documentation — *CUDA semantics* (Asynchronous execution, CUDA streams, CUDA Graphs) | PyTorch docs | 2026 | — | official-docs | https://docs.pytorch.org/docs/2.14/notes/cuda.html | 2026-09-24 |
| S30 | T2 | PyTorch 2.14 documentation — `torch.cuda.Event`, `torch.cuda.set_sync_debug_mode`, `torch.cuda.synchronize` | PyTorch docs | 2026 | — | official-docs | https://docs.pytorch.org/docs/2.14/generated/torch.cuda.set_sync_debug_mode.html | 2026-09-24 |
| S31 | T2 | PyTorch, *Performance Tuning Guide* (Migacz), "Avoid unnecessary CPU-GPU synchronization" and "Use CUDA Graphs" | PyTorch tutorials | 2025 | — | official-docs | https://docs.pytorch.org/tutorials/recipes/recipes/tuning_guide.html | 2026-09-24 |
| S32 | T2 | PyTorch, *A guide on good usage of non_blocking and pin_memory()* (Moens) | PyTorch tutorials | 2026 | — | official-docs | https://docs.pytorch.org/tutorials/intermediate/pinmem_nonblock.html | 2026-09-24 |
| S33 | T2 | PyTorch 2.14 documentation — `torch.compile` (`mode`) and *CUDAGraph Trees* | PyTorch docs | 2026 | — | official-docs | https://docs.pytorch.org/docs/2.14/user_guide/torch_compiler/torch.compiler_cudagraph_trees.html | 2026-09-24 |
| S34 | T2 | PyTorch 2.14 documentation — `torch.optim`, *Algorithms* (for-loop, foreach, fused) | PyTorch docs | 2026 | — | official-docs | https://docs.pytorch.org/docs/2.14/optim.html | 2026-09-24 |
| S35 | T3 | PyTorch v2.14.0 source — `aten/src/ATen/cuda/Sleep.cu`, `c10/cuda/CUDAStream.cpp`, `torch/cuda/__init__.py` | GitHub pytorch/pytorch | 2026 | tag v2.14.0 (2b3ec348) | source | https://github.com/pytorch/pytorch/blob/v2.14.0/aten/src/ATen/cuda/Sleep.cu | 2026-09-24 |
| S36 | T3 | PyPI JSON API — `torch` current release | PyPI | 2026 | torch 2.14.0 | source | https://pypi.org/pypi/torch/json | 2026-09-24 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | Crossref | `query.bibliographic=Deep Learning Workload Scheduling in GPU Datacenters A Survey` — the survey step, run first | Ye et al., ACM CSUR 56(6), 2024, DOI 10.1145/3638757, 126 citations; its causes of low utilisation are exclusive allocation and small operators, not host-side launch cost |
| 2 | 1 | arXiv | `ti:Deep AND ti:Learning AND ti:Workload AND ti:Scheduling AND ti:GPU AND ti:Datacenters` | arXiv:2205.11913v3, the survey's preprint, read in full |
| 3 | 1 | arXiv | abs and PDF of 1912.01703 | Paszke et al., v1 only, NeurIPS 2019; §5.2–§6.2 read; non-exclusive distribution licence, so Figure 1 is not reusable |
| 4 | 1 | Crossref | `works/10.1145/3620665.3640366` | Ansel et al., ASPLOS '24 vol. 2 pp. 929–947; author copy on pytorch.org read in full |
| 5 | 1 | arXiv | `ti:Nimble AND ti:Lightweight AND ti:Parallel AND ti:GPU` | arXiv:2012.02732v1, NeurIPS 2020; §2–§5 and appendices read |
| 6 | 1 | OpenAlex | `filter=cites:W3098625345` — forward chase from Nimble, sorted by citations | 15 citing works (Centauri, PiPAD, POS …), none squarely on launch overhead or CUDA Graphs |
| 7 | 1 | Semantic Scholar | `paper/arXiv:2012.02732/citations` — the same forward chase | 100 citing works; on-topic by count: ARK (NSDI '23), GPUReplay (ASPLOS '22), Opara (IEEE TC 2025); the details endpoint returned HTTP 429 twice |
| 8 | 1 | Crossref | `query.bibliographic=Understanding the Overheads of Launching CUDA Kernels` | no record; the ICPP '19 poster (≈2.5 µs CPU launch cost on a V100) has no DOI or archival record, so its number is not used |
| 9 | 1 | OpenAlex | `search=Empirical Study on Low GPU Utilization of Deep Learning Jobs` | Gao et al., W4394745249, DOI 10.1145/3597503.3639232; camera-ready read from the MSR copy (ACM DL served a bot challenge) |
| 10 | 1 | Crossref | `query.bibliographic` for Jeon ATC '19, Weng NSDI '22, Mohan PVLDB, Grape MICRO '23 | DOIs for Mohan and Grape; USENIX papers carry ISBNs only; all four read in full |
| 11 | 1 | OpenAlex | `filter=cites:W4394745249` — forward chase from Gao et al. | 24 citing works; kept Elvinger et al. (SoCC '25), which states the nvidia-smi limitation directly |
| 12 | 1 | arXiv | `id_list=2503.19779` (PyGraph) | v3, no journal reference; the author's page and USENIX proceedings show it published as GraCE, OSDI '26 |
| 13 | 1 | DBLP | `search/publ/api?q=PyGraph CUDA Graphs` | Anubis bot-challenge page, unusable; venue settled through USENIX instead |
| 14 | 1 | Crossref | `id 2501.09398`, kernel batching with CUDA Graphs | Ekelund et al., Euromicro PDP 2025, DOI 10.1109/PDP66500.2025.00019 |
| 15 | 4 | Google Scholar | `"nvidia-smi" GPU utilization misleading "SM" "one or more kernels"` (via web search) | RL-Scope (MLSys '21) and Elvinger et al.; practitioner blogs surfaced and were not used |
| 16 | 4 | Google Scholar | `Yeung "Towards GPU Utilization Prediction for Cloud Deep Learning"` (via web search) | HotCloud '20 — the one dissenting paper, which calls the counter a good estimate despite not measuring SMs |
| 17 | 4 | arXiv | PDF of 2102.04285v2 (RL-Scope camera-ready) | §4.3 and appendix B.2: nvidia-smi 100% during parallel self-play while each worker spent ~20 s of up to 5,080 s in kernels |
| 18 | 2 | NVIDIA docs | nvidia-smi *Utilization*; NVML `nvmlUtilization_t` | the time-fraction definition and the 1/6 s – 1 s sample period, identical in both |
| 19 | 2 | NVIDIA docs | DCGM *Profiling Metrics*; DCGM changelog | SM Activity definition and the N/5-blocks example; the 4.6.0 rename of field identifiers |
| 20 | 2 | NVIDIA docs | CUDA Programming Guide v13.4.2 §2.5, §3.1.3, §4.2, §5.2 | streams, events, default-stream semantics, implicit synchronization, graphs, `CUDA_LAUNCH_BLOCKING`, `CUDA_SCALE_LAUNCH_QUEUES` |
| 21 | 2 | NVIDIA docs | CUDA Runtime API 13.4 — Event, Stream, Device; API and stream sync behaviour | `cudaEventElapsedTime` resolution, the non-NULL-stream caveat, pageable copy rules, the spin/yield heuristic |
| 22 | 3 | NVIDIA Technical Blog | Gray 2019; Hoffman and Oh 2024 | per-kernel cost on a V100 three ways; near-constant graph launch on Ampere with CUDA 12.6 |
| 23 | 3 | NVIDIA docs | archived programming guides 11.8, 12.0, 12.3, 12.9 and release notes 12.0–12.8 | device graph launch from 12.0; IF/WHILE conditional nodes from 12.3; SWITCH and IF-else from 12.8 |
| 24 | 5 | PyTorch docs | CUDA semantics, `torch.cuda.Event`, `set_sync_debug_mode`, Tuning Guide, pin-memory tutorial, `torch.optim` | the async contract, the five named sync triggers, `non_blocking` semantics, the for-loop/foreach/fused ordering |
| 25 | 5 | PyTorch source | `Sleep.cu`, `CUDAStream.cpp`, `torch/cuda/__init__.py` at tag v2.14.0 | `_sleep` launches one thread in one block; the default stream is handle 0; pool streams are created non-blocking |
| 26 | 5 | PyPI JSON API | `torch` release metadata | current release 2.14.0, uploaded 2026-09-02 |
| 27 | 6 | PyTorch Blog | Accelerating PyTorch with CUDA Graphs (2021) | the framing that replay skips Python, C++ and driver dispatch; MLPerf v1.0 numbers |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | `nvidia-smi` defines GPU utilization as the percentage of the last sample period during which one or more kernels was executing on the GPU | S15 §Utilization | documentation read 2026-09-24; changelog up to v610 |
| L02 | That sample period is between 1/6 s and 1 s, depending on the product | S15, S16 | product-dependent; no per-product table is published |
| L03 | NVML's `nvmlUtilization_t.gpu` field carries the identical definition and is what `nvmlDeviceGetUtilizationRates` returns; NVIDIA states that much of `nvidia-smi`'s functionality is provided by NVML | S16; S15 intro | NVML API reference, latest (615), updated 2026-09-09 |
| L04 | Utilization queries are not supported on MIG-enabled GPUs, and with ECC on, GPU and memory utilization can read high during driver initialisation because of memory scrubbing | S15 | as documented 2026-09-24 |
| L05 | DCGM's SM Activity is the fraction of time at least one warp was active on an SM, averaged over all SMs; a warp stalled on memory still counts as active | S17 | DCGM docs, updated 2026-06-17 |
| L06 | DCGM's own example on an N-SM GPU: N blocks for the whole interval scores 1.0; N/5 blocks for the whole interval scores 0.2; N blocks for one fifth of the interval also scores 0.2 | S17 | simplified architectural view as DCGM states it |
| L07 | DCGM says an SM Activity of 0.8 or more is necessary but not sufficient for effective use, and below 0.5 likely indicates ineffective use | S17 | guidance attached to SM Activity, not to engine activity |
| L08 | DCGM 4.6.0 renamed the profiling field identifiers — `DCGM_FI_PROF_SM_ACTIVE` became `DCGM_FI_PROF_SM_UTIL_RATIO` (field 1002) — keeping the old names as deprecated aliases | S18 | DCGM ≥ 4.6.0; changelog read 2026-09-24 |
| L09 | DCGM profiling metrics are sampled at 1 Hz by default and no faster than every 100 ms | S17 | DCGM latest |
| L10 | Nsight Systems' *SMs Active* row is the percentage of cycles with at least one warp in flight, and NVIDIA notes 50% could mean all SMs for half the period or half the SMs for all of it | S19 | Nsight Systems v2026.5 |
| L11 | Nsight Systems' *Idle SM Unused Warp Slots* row lists "CPU starving the GPU" among its causes | S19 | Nsight Systems v2026.5 |
| L12 | In Nsight Systems, CUDA API calls appear as rows under the CPU thread that made them, and GPU work appears per context and per stream under a separate GPU node | S19 §CUDA Trace | Nsight Systems v2026.5 |
| L13 | The Philly trace study warns that its GPUs' utilization counter can only detect whether any SM is in use, so its figures are an upper bound on effective SM utilization | S06 §3.2 | Microsoft Philly, 2017; per-minute counters via Ganglia/NVML |
| L15 | RL-Scope found `nvidia-smi` reporting 100% GPU utilization during parallel self-play while each of 16 workers spent only about 20 s of a run of up to 5,080 s executing GPU kernels | S07 §4.3, App. B.2 | Minigo, 16 self-play workers; MLSys 2021 |
| L16 | A SoCC 2025 paper states that nvidia-smi/NVML utilization shows only the share of time a kernel is active and reveals nothing about how well kernels use the GPU | S08 §2.2 | arXiv v3 text |
| L17 | One workshop paper disagrees in part: it grants the counter does not measure SMs but calls it a good estimate for scheduling | S14 §2 | HotCloud 2020 |
| L18 | Microsoft studied 400 deep-learning jobs averaging 50% GPU utilization or less and found 706 issues; the largest categories were host-to-GPU data transfer (27.9%), batch size (25.6%) and synchronous checkpointing (16.4%) | S05 Table 1 | Microsoft internal platform, August 2021; utilization from DCGM, field not named |
| L19 | The same study found 84.99% of the issues fixable with small code or script changes | S05 abstract | as above |
| L20 | The same study found per-iteration logging and non-GPU tasks make utilization drop suddenly and recover, marking iteration boundaries | S05 §3.3 | as above |
| L21 | A CUDA stream behaves like a work queue: operations run in enqueue order, and one cannot overtake an operation queued before it | S20 §2.5.2, §2.5.5 | CUDA Programming Guide v13.4.2 |
| L22 | A kernel launch is asynchronous with respect to the host: the call returns without waiting for the kernel to finish or even to start | S20 §2.1.2.2 | v13.4.2 |
| L23 | Work in different streams may run concurrently only when there are no event dependencies, no implicit synchronization and enough resources | S20 §3.1.3 | v13.4.2 |
| L24 | The legacy default stream (stream 0) synchronizes with all other blocking streams: k1 on stream 1, k2 on the default stream and k3 on stream 2 run one after another | S20 §2.5.6.1; S24 §3 | legacy default stream, nvcc's default |
| L25 | Streams created with `cudaStreamNonBlocking` do not synchronize implicitly with stream 0 | S23 Stream Management | Runtime API 13.4 |
| L26 | Since CUDA 7 each host thread can have its own default stream, enabled with `nvcc --default-stream per-thread` | S20 §2.5.6.2 | v13.4.2 |
| L27 | An event records a timestamp when it reaches the front of its stream; recording one (`cudaEventRecord`) is asynchronous; the documented timing pattern is record, launch, record, synchronize, elapsed | S20 §2.5.3.3; S23 Event Management | v13.4.2 |
| L28 | `cudaEventElapsedTime` returns milliseconds with a resolution of about 0.5 µs | S23 Event Management | Runtime API 13.4 |
| L29 | If either event was last recorded in a non-NULL stream, the measured time may be greater than expected, because other work can run between the two records | S23 Event Management | Runtime API 13.4 |
| L30 | `cudaStreamWaitEvent` makes later work in a stream wait for an event, performed on the device where possible, so the host does not block | S23 Stream Management | Runtime API 13.4 |
| L31 | `cudaDeviceSynchronize` waits for all preceding work in all streams of all host threads; `cudaStreamSynchronize` waits for one stream | S20 §2.5.7 | v13.4.2 |
| L32 | By default a thread waiting for the device spins rather than yields when there are no more CUDA contexts than logical processors | S23 Device Management, `cudaSetDeviceFlags` | `cudaDeviceScheduleAuto` heuristic |
| L33 | A device-to-host `cudaMemcpy` returns only when the copy is complete, and a pageable host-to-device copy performs a stream synchronization before it starts | S24 §2 | Runtime API 13.4 |
| L34 | `cudaMemcpyAsync` from pageable memory can be synchronous with the host and does not overlap other work | S24 §2; S20 §2.5.2.3 | v13.4 |
| L35 | Any CUDA API call may block or synchronize for internal reasons such as resource contention, and that behaviour may change | S24 §2 | Runtime API 13.4 |
| L36 | `CUDA_LAUNCH_BLOCKING=1` forces GPU work to run synchronously from the CPU's view — a synchronization after every launch — and is meant for debugging | S22 §5.2.3.1; S20 §2.5.4.2 | v13.4.2 |
| L37 | NVIDIA documents that the launch queue is finite: `CUDA_SCALE_LAUNCH_QUEUES` scales the number of pending kernels or copies that can be enqueued on a device, without stating the base size | S22 §5.2.3.4 | v13.4.2; the base depth is undocumented |
| L38 | In PyTorch, GPU operations are asynchronous by default: a call enqueues work that may execute later; each device runs its queue in order, and PyTorch inserts the synchronization needed when data moves between CPU and GPU, so code behaves as if synchronous | S29 *Asynchronous execution* | PyTorch 2.14 |
| L39 | PyTorch's documentation states that timings taken without synchronization are wrong, and prescribes either `torch.cuda.synchronize()` or `torch.cuda.Event` | S29 *Asynchronous execution* | PyTorch 2.14 |
| L40 | `torch.cuda.Event.elapsed_time` reports milliseconds, and an event can be timed only if created with `enable_timing=True` | S30 | PyTorch 2.14 |
| L41 | `torch.cuda.synchronize()` waits for all kernels in all streams on a device | S30; S35 `torch/cuda/__init__.py` | PyTorch 2.14.0 |
| L42 | PyTorch's Tuning Guide names five kinds of synchronizing operation: `print` of a CUDA tensor, `.item()`, copies such as `.cuda()` and `.cpu()`, `.nonzero()`, and Python control flow on CUDA results | S31 | tutorial updated 2025-07-09 |
| L43 | The Tuning Guide's stated reason to avoid syncs is to let the CPU run ahead of the accelerator and keep its queue full | S31 | as above |
| L44 | `torch.cuda.set_sync_debug_mode("warn")` warns on synchronizing operations, and PyTorch labels it experimental and says not all syncs are caught | S30 | PyTorch 2.14 |
| L45 | `Tensor.to()` always issues `cudaMemcpyAsync`; with `non_blocking=False`, the default, PyTorch calls `cudaStreamSynchronize` after every copy | S32 | tutorial updated 2026-04-01 |
| L46 | On GPU, `cudaFree` may block its caller until all previously queued work on all GPUs completes, which is why PyTorch keeps its own caching allocator | S02 §5.3 | CUDA behaviour as described in 2019 |
| L47 | PyTorch queues kernels through CUDA streams so Python on the CPU overlaps operators executing on the GPU | S02 §5.2 | PyTorch as of 2019 |
| L48 | In a ResNet-50 training step traced by the PyTorch authors, GPU execution took about three times as long as CPU scheduling, keeping the GPU saturated | S02 §6.1 | 2× Xeon E5-2698 v4, one Quadro GP100 |
| L49 | PyTorch's default CUDA stream is stream 0 (the NULL handle); streams from its pool are created with `cudaStreamNonBlocking` | S35 `CUDAStream.cpp` | tag v2.14.0 |
| L50 | `torch.cuda._sleep(cycles)` launches a spin kernel with a grid of one block of one thread that busy-waits for the given number of clock cycles | S35 `Sleep.cu` L9–L34 | tag v2.14.0, CUDA path |
| L51 | PyTorch's for-loop optimizers are usually slower than foreach ones, which combine parameters into multi-tensors and save many sequential kernel calls; fused is faster still, and foreach is the default when applicable | S34 *Algorithms* | PyTorch 2.14 docs, updated 2026-05-10 |
| L52 | Nimble lists the host-side steps a framework runs before every GPU task: select an operator, check types and shapes, compute output shapes, pick a kernel, allocate memory, prepare arguments | S04 §2 | circa 2020 runtimes |
| L53 | In batch-size-1 inference on a V100, Nimble measured PyTorch leaving the GPU idle for up to 91% of the running time | S04 §3 | V100, PyTorch 1.4, CUDA 10.2 |
| L54 | Nimble's training measurements: marginal gains at ImageNet and BERT batch sizes, up to 3.61× with small CIFAR-10 inputs, because large batches hide scheduling overhead | S04 §5.3 | V100 |
| L55 | Gray's measurement on a V100 with CUDA 10.1: a 2.9 µs element-wise kernel over 500,000 floats cost 9.6 µs per launch with a synchronize after each, 3.8 µs when launches overlapped, and 3.4 µs as a CUDA graph | S26 | Tesla V100, CUDA 10.1, 20 kernels × 1,000 steps, wall clock ÷ 20,000 |
| L56 | In the same test, creating and instantiating the graph took about 400 µs, and the first graph launch was about a third slower than later ones | S26 | as above |
| L58 | A published DALLE2 inference trace at batch size 1 issued over 740 kernels totalling 3.4 ms of GPU time in a segment taking 14 ms end to end, about 75% of it attributed to CPU launch delays | S11 §2 | H100, no CUDA graph |
| L59 | NVIDIA defines a CUDA graph as operations joined by dependencies and defined separately from execution, submitted in three stages: definition, instantiation, execution | S21 §4.2, §4.2.2 | v13.4.2 |
| L60 | NVIDIA's stated motivation: each kernel put in a stream costs host setup that can be a significant fraction of a short kernel's time, while a graph pays that once at instantiation | S21 §4.2 | v13.4.2 |
| L61 | During stream capture it is invalid to synchronize or query a capturing stream, and an invalid operation invalidates the whole capture | S21 §4.2.2.1.2 | v13.4.2 |
| L62 | Changing a graph's topology requires re-instantiation; only node parameters can be updated in place | S21 §4.2.3 | v13.4.2 |
| L63 | Device graph launch arrived in CUDA 12.0; IF and WHILE conditional nodes in 12.3; SWITCH and IF-else in 12.8 | S25 | archived guides and release notes |
| L64 | On Ampere and later, repeat-launch CPU cost for straight-line graphs became nearly constant — about 2.5 µs plus about 1 ns per node — in CUDA 12.6, against 2 µs plus 200 ns per node in 11.8 | S27 | RTX 3060, Xeon Silver 4208, CUDA 11.8 vs 12.6 |
| L65 | The PyTorch team describes graph replay as skipping argument setup and dispatch in Python, C++ and the CUDA driver, with removing CPU overhead as the main benefit | S28 | PyTorch 1.10 era |
| L66 | In MLPerf Training v1.0, CUDA graphs made Mask R-CNN 1.70× faster and BERT 1.12× faster in NVIDIA's PyTorch submissions | S28 Table 1 | GPU model not stated in the post |
| L67 | PyTorch's CUDA-graph constraints: ops that synchronize CPU and GPU such as `.item()` are prohibited; CPU work is not captured and is skipped at replay; dynamic shapes are prohibited; allocations come from a graph-private memory pool | S29 *CUDA Graphs* | PyTorch 2.14 |
| L68 | PyTorch advises trying CUDA graphs when the network is graph-safe and at least somewhat CPU-limited | S29 *Why CUDA Graphs?* | PyTorch 2.14 |
| L69 | `torch.compile(mode="reduce-overhead")` uses CUDA graphs to cut Python overhead, may use more memory, and re-records a graph for each new input shape | S33 | PyTorch 2.14 |
| L70 | TorchInductor's ablation: turning cudagraphs off lowered its training speedup over eager from 1.45× to 1.37× | S03 Table 4 | A100, HuggingFace suite, float16 |
| L71 | Of 116 CUDA graphs taken from 63 TorchBench applications, 29 made performance worse, mainly from copying kernel parameters into static placeholders | S11 §2 | H100 NVL, PyTorch 2.4, CUDA 12.8 |
| L72 | For dynamic models, copying real inputs into a graph's placeholders cost up to 34% of execution time, each per-shape graph took 20–100 MB, and data-dependent control flow such as beam search could not be captured | S10 §1 | GPT-2, GPT-J, Wav2Vec2 on RTX 3090 |
| L73 | Batching iterative kernels into CUDA graphs had an optimal size of about 50–100 kernels, and the graph version only overtook plain launches after two to three batches | S12 §IV | A100, CUDA 12.3 |
| L74 | Per-iteration data stalls in DNN training can reach up to 65% of epoch time in CPU pre-processing | S13 Table 1 | nine DNNs, PyTorch with DALI, V100 servers |
| L75 | The current PyTorch release is 2.14.0, and the current CUDA Toolkit is 13.4 Update 1 | S36; S25 | read 2026-09-24 |
| L76 | A host-to-device copy overlaps a kernel only when a DMA engine is free, the copy runs on a separate non-default stream, and the source is in pinned memory | S32 | tutorial updated 2026-04-01 |
| L77 | The PyTorch CUDA Graphs team notes that dynamic shapes force CPU-GPU synchronization because they involve the framework's CPU-side memory management | S28 *BERT* | PyTorch 1.10 era |
| L78 | PyTorch builds CUDA graphs by stream capture: work issued to a capturing stream does not run on the GPU but is recorded into a graph that can be replayed | S29 *CUDA Graphs*; S21 §4.2.2.1.2 | PyTorch 2.14; CUDA v13.4.2 |
| L79 | PyTorch's whole-network capture recipe warms up a few iterations on a side stream, captures forward, backward and `optimizer.step()` into a `CUDAGraph` with static input tensors, then copies each new batch into those tensors and replays | S29 *Whole-network capture* | PyTorch 2.14 |
| L80 | `torch.compile`'s `backend=` argument defaults to TorchInductor | S03 §3 | PyTorch 2 as described at ASPLOS '24 |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S02 | Figure 1 | Intuition / L47–L48 | a real CPU/GPU trace of the first operators of a ResNet-50 step | arXiv non-exclusive distribution licence 1.0; no reuse right granted | https://arxiv.org/abs/1912.01703 | do not reuse — the worked example's own timeline (FIG_02) carries the same point with numbers the reader can check |
| F2 | S26 | profiler timelines | Launch cost / L55 | shows gaps between kernels | NVIDIA blog, no licence stated | https://developer.nvidia.com/blog/cuda-graphs/ | do not reuse — FIG_08 charts the measured numbers instead |

## Literature and disagreement

The literature on this subject is operational rather than theoretical, and the sweep found it in
cluster trace studies (S05, S06, S09), framework papers (S02, S03, S04) and CUDA-graph systems
papers (S10, S11, S12). No survey covers host-side launch overhead or the semantics of the
utilization counter; the one survey found (S01) attributes low utilization to allocation and
small operators.

**The contested point the post must carry.** NVIDIA documents utilization as a *time fraction*
(L01). RL-Scope measured it reading 100% on a GPU executing kernels for a few percent of the
time (L15), which is not what a strict time fraction would report. Jeon et al. describe the
counter as detecting only whether *any* SM is in use (L13). The post states NVIDIA's definition,
states the measurement that contradicts it in practice, does not resolve which is right on a given
GPU, and ships `lab/util_probe.py` to answer it on the reader's own hardware.

## Open questions

- **The launch queue's base depth.** `CUDA_SCALE_LAUNCH_QUEUES` proves it is finite (L37); the
  size is undocumented. A forum report of about 1,022 queued kernels on an A100 is T4 and is not
  used. The model assumes an unbounded queue and the article says so.
- **How NVML actually samples.** The documentation defines a time fraction; the measurement in
  L15 behaves otherwise. No NVIDIA source explains the sampling mechanism. Left open; the lab
  measures it.
- **Whether PyTorch's stream 0 is the legacy or per-thread default stream.** The source shows the
  NULL handle (L49) and no per-thread build flag was found in the files searched; PyTorch never
  says "legacy". The post says "stream 0" and describes legacy semantics as CUDA's, not PyTorch's.
- **Gao et al.'s DCGM field.** The paper does not name whether its utilization was the device
  counter or SM Activity. Its percentages are used only as causes, never as a utilization level.
