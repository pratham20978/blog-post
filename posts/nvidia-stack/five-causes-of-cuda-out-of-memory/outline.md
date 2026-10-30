# Outline — Five Causes of One "CUDA Out of Memory"

Series `nvidia-stack`, part 4 of 16. Private build artifact.

## Brief

- **Tier L3.** Five distinct causes plus the allocator mechanism plus the ledger arithmetic plus a
  working diagnosis procedure; the smallest honest worked example is five runs of one model, which
  needs a page. Adjacent option: L2 by dropping the unified-memory section and the math, which would
  leave the decision tree unexplained.
- **Difficulty intermediate.** Assumes the reader trains models in PyTorch, has seen the message, and
  knows the CPU queues GPU work asynchronously (Part 3). Adjacent option: advanced, by dropping the
  allocator walk-through.
- **Lab grade G3 · needs one NVIDIA GPU (this series' Tier B), captured.** AR-01 answered `grant` on
  2026-10-30 with a LAN host: an NVIDIA GB10 (Dell Pro Max with GB10), 121.63 GiB unified with the CPU.
  E1 and E2 run from `captures.json` with the G1 `diagnose.py`; E3 and E4 need the GPU.
- **The five causes** (plan objectives 10 and 11): capacity, fragmentation, a retained autograd graph,
  another process (or an orphan), and memory this process holds outside PyTorch. "Reserved versus
  allocated" is the vocabulary that reads all five, not a sixth cause: the allocator flushes its own
  cache before it raises (L15), so its cache starves only other consumers.

## Checkpoint A — recorded, not held

The owner pasted the plan block and said "build" (series convention: end to end). What the post can
honestly claim, from the ledger and the capture:

- **Measured on the GB10** (captures.json, 2026-10-30T11:44:17Z): the five messages and their numbers;
  the fixes held; `empty_cache()` then retry failed twice; the FAQ pattern cost 0 bytes per training step
  and the evaluation pattern 1.55 GiB per batch; non-PyTorch memory by stage (173 MiB context lazy,
  943 MiB eager, +548 MiB NCCL on one rank); a Unix zombie released 6.6 GiB 0.13 s after exiting, unreaped;
  an orphan reparented to systemd kept 6.17 GiB; CUDA free equals MemFree on this GPU; the legacy env
  variable wins.
- **Emulated, and said so:** the 24 GiB card. Every message carries "allowed" and the GB10's real total.
- **Documented, not measured:** prevalence (L01–L02), ZeRO and GMLake fragmentation rates (L09–L10),
  lazy-loading defaults (L32), NVML semantics (L34), DGX Spark guidance (L36–L37), PR history (L22–L23).
- **Not claimed:** typical context sizes on discrete cards, NCCL's breakdown, container PID behaviour
  (no primary source found; stated as a reason NVML PIDs may not resolve, without a number).

## Checkpoint B — recorded, not held

Outline below, built end to end on the owner's "build".

## Sections and budget (target ~6,000 words of prose; References add ~900)

| # | Heading | Words | Job | Figures |
|---|---|---|---|---|
| 0 | Insights + who + where the numbers come from | 200 | the answer, and the GB10/emulation notice | — |
| 1 | Why this matters | 200 | 8.8% of Philly failures; most capacity; the empty GPU afterwards | — |
| 2 | The problem: one message, six numbers | 450 | every field of the message and what it measures | FIG_01 |
| 3 | Worked example: one 20 GiB model, five failures | 850 | the model's 20.00 GiB arithmetic, the card, five runs, the table, the tree | FIG_02, FIG_03 |
| 4 | Intuition: the card is a ledger | 300 | five lines; where the ledger analogy breaks (pieces) | — |
| 5 | What does the caching allocator do with freed memory? | 600 | segments, blocks, pools, rounding, best fit, split, retry chain, empty_cache | FIG_04 |
| 6 | Why does a 256 MiB request fail with 4.63 GiB free? | 750 | the 128 MiB tails, isolated deaths, literature, expandable segments, the knobs | FIG_05, FIG_06 |
| 7 | What keeps memory growing from step to step? | 450 | retained graph; growth first; the FAQ measured | FIG_07 |
| 8 | Who else is holding the card? | 650 | other processes, graphics, orphans vs zombies; this process outside PyTorch | FIG_08 |
| 9 | What changes when GPU memory is system memory? | 300 | GB10: total = MemTotal, free = MemFree, CPU allocations, nvidia-smi | FIG_09 |
| 10 | The math: the ledger in symbols | 350 | identities, the deficit, the rule; collapse back to run 4 | — |
| 11 | Implementation: reading the message in code | 400 | catch, stats keys, growth, diagnose.py, snapshot | — |
| 12 | Limitations and common mistakes | 350 | emulation; empty_cache; env var; max_split_size_mb; graphs; containers | — |
| 13 | Key takeaways | 120 | five claims | — |
| 14 | Try it yourself | 220 | three exercises from the article alone | — |
| 15 | References | — | Lab downloads, Sources | — |

## Numbers each section uses (all from captures.json unless keyed)

- Model: 16 × Linear(8192, 8192) + GELU, fp32 weights, Adam (foreach). Weights 4 GiB, gradients 4,
  Adam 8, foreach temporaries 4 → optimizer-step peak 20.00 GiB; forward peak 18.38; step 1.3 s.
- Card 24.00 GiB emulated; non-PyTorch 335.92 MiB → allowed 23.67 GiB.
- Run 1 fragmentation (batch 12288, default): optimizer step 0; request 256 MiB; allocated 19.00;
  reserved-unallocated 4.63 GiB = 37 × 128 MiB; this process 23.96; retry after empty_cache failed
  (released 3.00 GiB, the 12 freed foreach temporaries).
- Run 2 capacity (batch 12288, expandable): step 0 fine; step 1 forward; request 384 MiB; allocated 23.25;
  unallocated 252 MiB, largest free 16 MiB; retry released 0 and failed; checkpointing fixes it (peak 20.00).
- Run 3 retained (validation batch 1536, no no_grad): 12.00 → 13.55 → … → 22.83 GiB at batch starts;
  OOM in batch 7; request 48 MiB; unallocated 514 MiB = 32 × 16 MiB; +1.55 GiB per batch = 33 × 48 MiB.
- Run 4 other process: orphan PID (ppid 1, systemd, state S) 6.17 GiB; allowed 17.50; request 256 MiB
  at optimizer step 0; "Process N has 6.17 GiB memory in use".
- Run 5 non-PyTorch: 4 GiB pool by cuMemAlloc; this process 23.83, reserved 19.50 → 4.33 GiB outside;
  allowed 19.67.
- Inventory: 173.42 / 241.67 / 335.92 / 343.92 / 891.92 / 891.92 / 503.92 MiB; eager 942.92, 1256.92 MiB.
- Unified: CUDA free 104.25 = MemFree 104.25; MemAvailable 114.45; Cached 9.18; after 8 GiB CPU tensor
  96.22 / 96.22 / 106.43; graphics processes 792.22 MiB (Xorg 250.20, firefox 278.78, gnome-shell
  120.65, code 98.48, nautilus 44.12); NVML device memory info NOT_SUPPORTED.
- Zombie: Z at 0.271 s still listed; at 0.404 s not listed, MemFree +6.61 GiB; reaped after.

## Figure plan (route gate run per figure)

| Fig | Section | One thing it must communicate | Route | Why |
|---|---|---|---|---|
| 1 | Problem | each field of a real message, and which cause it rules in | capture | Q2 — the run's own message, verbatim, annotated |
| 2 | Worked example | five runs on one card: where the missing bytes sit in each | chart | Q1 — measured ledger per run, stacked to one scale |
| 3 | Worked example | the order to read the numbers, with each run at its leaf | mermaid | Q3 — 11 nodes: five questions, five causes and a start |
| 4 | Allocator | a request's path through rounding, pools, best fit, split, cudaMalloc and the retry chain | mermaid | Q3 — 12 nodes with two retry loops |
| 5 | Fragmentation | 37 segments of 384 MiB, each a live 256 MiB head and a free 128 MiB tail, beside the 256 MiB that fails | plot | Q1 — measured snapshot drawn to scale |
| 6 | Fragmentation | separate segments cannot merge tails; one expandable segment maps pages and can | placed | Q4 — address ranges to scale, physical pages under virtual |
| 7 | Retained graph | allocated memory per validation batch, with and without no_grad, against the allowance | chart | Q1 — measured series |
| 8 | Who else | what one process holds outside PyTorch, stage by stage, lazy and eager | chart | Q1 — measured bars |
| 9 | Unified | CUDA free tracks MemFree, not MemAvailable; a CPU tensor shrinks it | chart | Q1 — measured before/after |

No paper figure is reused (ledger F1, F2).

## Term map

| Term | First section | What | Why here | When it matters |
|---|---|---|---|---|
| out-of-memory error (OOM) | Insights | `torch.OutOfMemoryError` raised by the allocator | the message being decoded | every failure here |
| caching allocator | Problem | PyTorch's GPU memory manager that keeps freed memory for reuse | it owns reserved and allocated | always on unless disabled |
| segment / block | Problem | one cudaMalloc result / a piece of a segment handed to a tensor | fragmentation lives between them | reading snapshots |
| allocated / reserved / reserved but unallocated | Problem | tensor bytes / segment bytes / the difference | the message's last two numbers | fragmentation vs capacity |
| NVML | Problem | NVIDIA's management library; nvidia-smi reads it | the per-process lines come from it | other-process diagnosis |
| compute vs graphics process | Who else | NVML's two process lists | the message names only compute ones | desktop GPUs |
| non-PyTorch memory | Problem | this process's GPU memory outside the allocator | the "Including non-PyTorch memory" line | libraries, context, NCCL |
| CUDA context | Who else | per-process driver state on the device, incl. loaded kernels | always outside PyTorch | the baseline |
| lazy loading | Who else | loading kernel modules on first use | shrinks the context | eager vs lazy |
| memory fraction / allowed | Worked example | `set_per_process_memory_fraction` cap | how the card is emulated | the "allowed" clause |
| autograd graph / saved tensors | Retained | what backward needs, kept by outputs with history | the leak | eval loops |
| expandable segments | Fragmentation | segments that grow by mapping pages into reserved VA | the fix the message names | variable shapes |
| virtual memory management APIs | Fragmentation | cuMemCreate, cuMemAddressReserve, cuMemMap | how segments grow | — |
| max_split_size_mb | Fragmentation | stop splitting large blocks | older fix, last resort | — |
| PYTORCH_ALLOC_CONF | Fragmentation | allocator settings variable; legacy alias wins | the configuration trap | both set |
| orphan / zombie / subreaper | Who else | Unix process states | which one holds memory | leftover jobs |
| unified memory / integrated GPU | Unified | GPU memory that is system memory | GB10 measurements | DGX Spark, Jetson |
| num_alloc_retries | Allocator | count of flush-and-retry | the near-miss signal | throughput |
| memory snapshot | Implementation | allocator state dump for pytorch.org/memory_viz | seeing slivers | fragmentation |
| activation checkpointing | Worked example | recompute activations in backward | the capacity fix | big batches |

## Earlier parts named (plain text; the owner adds links)

- Part 3, "Why Your GPU Is Idle at 100% Utilization" — the prerequisite (CPU runs ahead; a free on the
  CPU precedes the GPU's last use). Not live (404 on 2026-10-30).
- Part 1, "What the NVIDIA Stack Actually Is" — once, for where the CUDA context lives (live).
- Later parts: "later in this series" only.
