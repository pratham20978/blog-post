---
title: "Five Causes of One “CUDA Out of Memory”"
slug: five-causes-of-cuda-out-of-memory
date: 2026-10-30
updated: 2026-10-30
summary: "PyTorch prints one CUDA out-of-memory error for five unrelated causes. The numbers in the message tell them apart, and empty_cache() fixes none of them."
tags: [machine-learning, cuda, pytorch, gpu, memory-management, debugging]
category: machine-learning
series: nvidia-stack
series_position: 4
tier: L3
difficulty: intermediate
prerequisites: ["a PyTorch training loop run on a GPU", "the CPU queues GPU work ahead of it"]
reading_minutes: 29
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/five-causes-of-cuda-out-of-memory"
---

![A 256 MiB request above 37 memory segments, each a live block beside a free tail too small to hold it](COVER)

> [!NOTE]
> **Insights** — PyTorch's `CUDA out of memory` error is a ledger, not a verdict: after the first line it prints how much memory PyTorch has allocated, how much it holds without using, how much this process holds in all, and which other processes hold the rest. Five unrelated causes share that first line — a workload too big for the card, fragmentation, a retained autograd graph, another process, and memory outside PyTorch — and each one inflates a different number. Check whether memory grows between iterations first, then whether *reserved but unallocated* covers the request, then the other holders; what remains is capacity. `torch.cuda.empty_cache()` fixes none of the five for the process that crashed.

**Level:** intermediate · **You need:** a PyTorch training loop you have run on a GPU, and the idea that the CPU queues GPU work ahead of it · **Time:** ~29 min

**Jump to:** [the message](#the-problem-one-message-six-numbers) · [five failures](#worked-example-one-20-gib-model-five-failures) · [the allocator](#what-does-the-caching-allocator-do-with-freed-memory) · [fragmentation](#why-does-a-256-mib-request-fail-with-463-gib-free) · [retained graphs](#what-keeps-memory-growing-from-step-to-step) · [other holders](#who-else-is-holding-the-card) · [unified memory](#what-changes-when-gpu-memory-is-system-memory) · [code](#implementation-reading-the-message-in-code)

> [!IMPORTANT]
> **Where the numbers come from.** Every number this post calls *measured* comes from its lab, run on 2026-10-30 on an NVIDIA GB10 (a Dell Pro Max with GB10) with PyTorch 2.15.0, the newest release that day. <!-- L40 --> The GB10's GPU shares 121.63 GiB with its CPU, so filling it would starve the whole machine. The lab instead emulates a **24 GiB card**: before every phase of a step it caps PyTorch's allocator, with `torch.cuda.set_per_process_memory_fraction`, at 24 GiB minus whatever the rest of the card holds. <!-- L29 --> The allocator, its decisions and its error messages are real; only the card's size is emulated. That is why each message below reports a total capacity of 121.63 GiB and an "allowed" clause, two things a 24 GiB card would not print. Every other number carries a source.

## Why this matters

Over three weeks in October 2018, 434 of 4,960 failed jobs on Microsoft's internal deep-learning platform died of a GPU out-of-memory error: 8.8% of all failures, and the largest category specific to deep learning. <!-- L01 --> The study that counted them traced most of the ones it examined to a batch or a model too large for the card. <!-- L02 --> That is the cause everyone assumes, and the error message makes every other cause look exactly like it.

The first line never changes: `CUDA out of memory. Tried to allocate 256.00 MiB.` A run whose memory is fragmented, a run that leaks one evaluation batch at a time, and a run sharing the card with a forgotten process print the same line and need opposite fixes. Halving the batch fixes the first, only postpones the second, and does nothing for the third. By the time you open `nvidia-smi`, the failed process has exited and the card looks empty; the numbers in the message are the only record of what held the memory.

## The problem: one message, six numbers

Here is one of the lab's messages, with a line break after each sentence:

```text
CUDA out of memory. Tried to allocate 256.00 MiB.
GPU 0 has a total capacity of 121.63 GiB of which 79.59 GiB is free.
Including non-PyTorch memory, this process has 23.96 GiB memory in use.
23.67 GiB allowed;
Of the allocated memory 19.00 GiB is allocated by PyTorch,
and 4.63 GiB is reserved by PyTorch but unallocated.
If reserved but unallocated memory is large try setting PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True ...
```

Reading it needs one piece of vocabulary. PyTorch does not ask the CUDA driver for memory each time it makes a tensor. Its **caching allocator** — the component that manages GPU memory for every tensor — asks the driver for large regions, called **segments**, with `cudaMalloc`, hands out pieces of them, called **blocks**, to tensors, and keeps freed blocks for the next tensor instead of returning them. Memory in its segments is **reserved**; the part inside blocks that live tensors use is **allocated**. The gap between the two, *reserved but unallocated*, is memory PyTorch holds and no tensor is using.

The message reports six numbers, measured by three different instruments: <!-- L16 -->

1. **The request**, `Tried to allocate`: the size of the new block or segment the allocator needed — not always the tensor's size, because the allocator rounds requests up.
2. **Total and free**: what `cudaMemGetInfo`, the CUDA runtime's device-wide query, reports for the whole GPU, every process included.
3. **Other processes**, one `Process N has X memory in use` line each, from NVML — the NVIDIA Management Library, the driver's monitoring interface that `nvidia-smi` is built on. This message has none.
4. **This process**, `Including non-PyTorch memory`: NVML's figure for the crashing process, which counts everything it holds on the GPU, PyTorch's reserved memory and anything else.
5. **Allowed**: present only when a memory fraction caps PyTorch, as the lab's emulated card does.
6. **Allocated by PyTorch** and **reserved but unallocated**: the allocator's own books.

![The fragmentation run's message, each of its numbers labelled with the instrument behind it and the cause it can reveal](FIG_01)
*Figure 1. One message, three instruments: the driver measures the device, NVML the processes, and the allocator its own books. Each cause of the error inflates a different line.*

In Figure 1 most of the evidence is in the last four lines, and most people stop reading after the first. The problem is to say, from these numbers, which of five causes filled the card.

## Worked example: one 20 GiB model, five failures

Training memory has three parts — the parameters, the model states that train them, and the activations — the same split a recent survey of the field uses. <!-- L03 --> The model is a stand-in whose three parts you can work out by hand: 16 layers of `Linear(8192, 8192)`, each followed by a GELU activation, in 32-bit floats, trained with Adam. One layer's weights are 8,192 × 8,192 × 4 bytes = 256 MiB, so the 16 layers hold 4 GiB. Gradients take another 4 GiB, and Adam's two running averages per weight take 8 GiB more. At a batch of 6,144 rows each layer saves two activations of 192 MiB for the backward pass, 6 GiB in all.

The peak is not where most people look for it. It lands in the optimizer step. PyTorch's default Adam is its *foreach* implementation, which updates all 16 weight tensors in one batched pass, <!-- L41 --> and here it briefly needed temporary tensors the size of the weights: 4 + 4 + 8 + 4 = **20.00 GiB**, measured. The forward pass peaks at 18.38 GiB. That is the 20 GiB model. On the emulated 24 GiB card, after this process's CUDA context — the driver's per-process state on the GPU, measured below — the allocator may use 23.67 GiB. Five runs then make it fail:

| Run | What changed | Failed at | Request | Allocated by PyTorch | Reserved, unallocated | Other processes | Outside PyTorch |
|---|---|---|---|---|---|---|---|
| 1 | batch doubled to 12,288 | optimizer, step 0 | 256 MiB | 19.00 GiB | **4.63 GiB** | — | 0.33 GiB |
| 2 | same batch, expandable segments on | forward, step 1 | 384 MiB | **23.25 GiB** | 0.25 GiB | — | 0.33 GiB |
| 3 | evaluation loop without `no_grad` | batch 7 | 48 MiB | 23.16 GiB | 0.50 GiB | — | 0.33 GiB |
| 4 | a leftover process holds 6 GiB | optimizer, step 0 | 256 MiB | 17.50 GiB | 0.00 GiB | **6.17 GiB** | 0.33 GiB |
| 5 | a library in the process holds 4 GiB | optimizer, step 0 | 256 MiB | 19.50 GiB | 0.00 GiB | — | **4.33 GiB** |

"Outside PyTorch" is the message's *this process* minus PyTorch's reserved memory: for run 1, 23.96 − (19.00 + 4.63) = 0.33 GiB, the CUDA context. Each run's bold number is the one that discriminates it.

**Run 1, fragmentation.** Doubling the batch makes every activation 384 MiB. During step 0's backward pass those activations are freed into the cache, and the 256 MiB gradients and Adam states are cut out of the freed 384 MiB blocks, leaving 128 MiB tails between live tensors. When the optimizer asks for one more 256 MiB, PyTorch holds 4.63 GiB unused — more than 18 times the request — but in pieces too small for it, and the card is full.

**Run 2, capacity.** With expandable segments (explained below) step 0 completes, and step 1 fails in the forward pass. A 12,288-row forward pass needs about 24.75 GiB: 12 GiB of weights and Adam state plus 12.75 GiB of activations. PyTorch has 23.25 GiB allocated and 0.25 GiB unallocated, none of it in a piece larger than 16 MiB, and nothing else holds memory. Recomputing activations during the backward pass instead of storing them — **activation checkpointing**, a trade of compute for memory <!-- L12 --> — ran the same batch for three steps at a 20.00 GiB peak.

**Run 3, a retained graph.** An evaluation loop sums `total = total + loss` without `torch.no_grad()`. Allocated memory at the start of each batch reads 12.00, 13.55, 15.09, 16.64, 18.19, 19.73, 21.28, 22.83 GiB, and the eighth batch fails asking for 48 MiB. Its message shows 514 MiB reserved but unallocated, more than ten times the request, which on its own reads as fragmentation. The growth is the real story.

**Run 4, another process.** Before training, a process left over from an earlier run holds 6 GiB. Its parent was killed, so it now belongs to `systemd`, process 1, and it does nothing. The message names it: `Process 189145 has 6.17 GiB memory in use`.

**Run 5, memory outside PyTorch.** A library in the same process holds a 4 GiB pool, which PyTorch's books cannot see. The message says this process has 23.83 GiB in use while PyTorch reserves 19.50 GiB: 4.33 GiB is held by something else.

![Six bars on one 24 GiB scale, a baseline and five failed runs, each split by who held the memory, the request past the edge](FIG_02)
*Figure 2. The same card, filled five ways. In every failing run the free part is smaller than the request, and a different segment of the bar is the one that grew.*

Figure 2 shows why the first line of each message is useless: every bar ends at the right edge of the card, and only the segment that grew differs. Each fix removed its own failure. Expandable segments carried run 1 past step 0, into run 2's capacity limit; checkpointing ran run 2's batch; `no_grad` ran run 3's loop to the end; stopping the leftover process and freeing the pool each let training complete. Calling `torch.cuda.empty_cache()` and retrying, the usual first reflex, failed in both runs it was tried in.

The order you read the numbers in matters, and run 3 shows why. Its message passes the fragmentation test, so growth has to be checked before anything else:

![Decision tree: growth means a retained graph, then unallocated at least the request means fragmentation, then other holders, then capacity](FIG_03)
*Figure 3. Read the message in this order. A leak eats the headroom until the last small request fails among slivers, so its message also looks fragmented.*

## Intuition: the card is a ledger

Think of the card as a ledger with five lines: what other processes hold, what this process holds outside PyTorch, what PyTorch holds in live tensors, what PyTorch holds and has not handed out, and what is free. A request fails when it is larger than the free line. Every cause is one line that grew: capacity and the retained graph grow the allocated line, one all at once and one an iteration at a time; fragmentation grows the held-but-unused line; the last two causes grow lines PyTorch does not own.

The analogy breaks at one line, and that break is the reason the error is confusing. A ledger's entries are amounts; memory is a range of addresses. Run 1's 4.63 GiB is not one amount but 38 separate pieces, 37 of them 128 MiB tails, and a tensor needs one contiguous piece. A ledger that balances can still refuse a request, and the allocator's rules decide when it does.

## What does the caching allocator do with freed memory?

PyTorch caches because returning memory is expensive: on a GPU, `cudaFree` can block its caller until all work already queued on all GPUs has finished. <!-- L04 --> The allocator therefore builds up a cache of segments as the program asks for memory and reuses them without calling CUDA again. It reuses a freed block at once even though, as part 3 of this series, *Why Your GPU Is Idle at 100% Utilization*, showed, the CPU runs ahead of the GPU and the kernel that last used the block may still be queued. That is safe because the allocator keeps one pool per CUDA stream, a queue in which the GPU runs work in order: a block freed on a stream is reused only on the same stream, so the next kernel to use it runs after the last one that did. <!-- L05 --> Taking memory as it goes, instead of all of it at start-up, also leaves room for other GPU libraries in the same process. <!-- L06 -->

Every request is rounded before anything else. At 2.15.0 the minimum is 512 bytes; requests up to 1 MiB come from a small pool of 2 MiB segments; requests between 1 and 10 MiB are served from 20 MiB segments; larger requests get their own segment, rounded up to 2 MiB. <!-- L13 --> This is why `Tried to allocate` can exceed the tensor: a 3 MiB tensor that needs a new segment is reported as 20.00 MiB.

Then the allocator searches its pool for the smallest free block that fits, **best fit**, and splits it if the remainder is worth keeping. <!-- L14 --> Only when no cached block fits does it call `cudaMalloc` for a new segment. Figure 4 follows a request through the whole path, including what happens when the driver says no:

![PyTorch's allocator path: round, take the smallest free block and split it, else cudaMalloc, else free cached blocks, retry, raise](FIG_04)
*Figure 4. The allocator raises only after giving back every cached segment it can. Whatever it still holds when it raises is in segments a live tensor pins.*

If `cudaMalloc` fails, the allocator gives cached memory back and tries again. With `max_split_size_mb` set it first frees just enough large cached blocks for the request; in every configuration, unless a CUDA graph is being captured, it then waits for pending work, frees every cached block that is not split, and retries once more. <!-- L14 --> <!-- L15 --> Only then does it raise. That final flush is counted in `torch.cuda.memory_stats()["num_alloc_retries"]`, and it is costly even when it succeeds: the PyTorch FSDP (Fully Sharded Data Parallel) paper calls the blocking sequence of `cudaFree` calls a *cudaMalloc retry*, says it greatly degrades training throughput, and names that counter as the way to spot it. <!-- L11 --> When the lab's runs failed, the counter stood between 1 and 3: the flush that failed, plus earlier ones that had succeeded.

The consequence is the most useful fact in this post. **By the time the error is raised, the allocator has already given back every cached segment it could; what the message calls reserved but unallocated is only free space inside segments that still hold a live tensor.** <!-- L15 --> So `torch.cuda.empty_cache()` cannot help the process that crashed. In run 2 it released 0 bytes and the retried forward pass failed again. In run 1 it released 3.00 GiB — the failed operation's own half-built outputs, freed while the error unwound — and the retried optimizer step failed again. The documentation says the same thing from the other side: `empty_cache()` frees cached memory for *other* GPU applications, and cached memory shows as used in `nvidia-smi`. <!-- L26 --> A large reserved number after a peak is the cache doing its job, not a leak.

## Why does a 256 MiB request fail with 4.63 GiB free?

Fragmentation is the inability to reuse memory that is free, and its external form is free blocks too small for the sizes requested. Its cause is *isolated deaths*: a free area whose neighbours are still in use cannot merge into anything larger. <!-- L07 --> For general-purpose programs the problem was nearly settled long ago: on eight real C and C++ programs, best fit averaged under 1% fragmentation, though its authors warned that unusual allocation behaviour might be missing from their sample. <!-- L08 --> Deep-learning training is that unusual behaviour. The authors of ZeRO, the Zero Redundancy Optimizer, saw out-of-memory errors with more than 30% of memory still free when training very large models, and traced them to short-lived and long-lived tensors interleaving. <!-- L09 --> GMLake measured up to 30% fragmentation under PyTorch's best-fit allocator when memory-saving techniques were on. <!-- L10 -->

Run 1 shows the mechanism at small scale. The allocator's snapshot at the failure lists 37 free blocks of exactly 128 MiB, each sitting in a 384 MiB segment next to a live 256 MiB tensor:

![Run 1's segments to scale: 37 of 384 MiB, each a live 256 MiB tensor beside a free 128 MiB tail, and a 256 MiB request](FIG_05)
*Figure 5. 4.63 GiB free in 38 pieces — 37 tails of 128 MiB and one small block — and no free block of 256 MiB. Each tail is an isolated death: its neighbour is live state that never goes away.*

Here is how Figure 5 came about. Step 0's backward pass freed 384 MiB activation blocks while it allocated 256 MiB gradients, and when the optimizer step created Adam's state it asked for more 256 MiB blocks. Best fit gave both the smallest blocks that fit, the freed 384 MiB ones, and split off each 128 MiB remainder. The heads are long-lived: Adam's state lives for the whole run. Each tail is pinned between its head and the end of its segment, and blocks in different segments can never merge. <!-- L20 --> When the optimizer then asked for its temporary 256 MiB tensors, twelve of sixteen fit and the thirteenth did not.

The fix the message suggests changes what a segment is. CUDA's virtual memory management API separates physical memory from addresses: `cuMemCreate` makes a physical allocation with no address, `cuMemAddressReserve` reserves a range of addresses with no memory behind it, and `cuMemMap` joins the two. <!-- L35 --> With `expandable_segments:True`, PyTorch reserves a range of 1⅛ times the device's memory per stream and maps physical pages into it as it grows (Figure 6) — 2 MiB pages for the small pool, 20 MiB for the large one. <!-- L18 -->

![Separate cudaMalloc segments whose free tails cannot merge, beside one expandable segment whose free space merges at its end](FIG_06)
*Figure 6. Separate segments trap their tails; one growing range lets neighbouring free space merge, and lets whole free pages move to where the next request needs them.*

With it on, run 1's step 0 completed at a 20.00 GiB peak. It is not a cure-all. Free space still cannot merge across a live block, so long-lived and short-lived tensors interleaved in one pool can still fragment it, <!-- L20 --> and memory in expandable segments cannot be shared with another process over CUDA IPC (inter-process communication). <!-- L19 --> At 2.15.0 it is off by default and documented as experimental. <!-- L21 --> It arrived in March 2023, and making it the default was proposed in April 2023 and again in July 2024. <!-- L22 -->

The older advice was `max_split_size_mb`, which stops the allocator splitting blocks above a size. The documentation calls it a last resort with a cost "from zero to substantial", <!-- L25 --> and PyTorch stopped recommending it first in November 2023, after projects that set it to fix fragmentation saw throughput drop later from freeing empty segments. <!-- L23 --> Keeping shapes stable — padding to a few fixed batch or sequence sizes — avoids the problem without any setting.

One trap sits in the setting itself. The documentation calls `PYTORCH_ALLOC_CONF` the variable and `PYTORCH_CUDA_ALLOC_CONF` an alias kept for compatibility, but the parser reads `PYTORCH_CUDA_ALLOC_CONF` first and uses only the first one it finds. <!-- L24 --> The lab set both to opposite values, twice: the legacy name won both times. Set one, and confirm it took effect: each segment in `torch.cuda.memory_snapshot()` carries `is_expandable`.

## What keeps memory growing from step to step?

When a tensor is computed from tensors that require gradients, PyTorch records the operations — the **autograd graph** — and keeps the inputs the backward pass will need, its **saved tensors**. `backward()` frees them as it goes. Anything that keeps a reference to the result keeps its graph alive, and with it every tensor the graph saved.

Run 3's evaluation loop keeps all of them. Each batch of 1,536 rows saves 33 tensors of 48 MiB — the input of every linear layer, the input of every GELU, and the input of the final square — and `total = total + loss` holds each batch's graph for the rest of the loop. That is 1,584 MiB, or 1.55 GiB, per batch:

![Allocated memory per evaluation batch: rising 1.55 GiB a batch from 12.00 to 22.83 GiB and failing, or flat at 12.00 with no_grad](FIG_07)
*Figure 7. A retained graph is a slope. The eighth batch fails with 514 MiB unused, a message that alone would point at fragmentation.*

The same loop under `torch.no_grad()`, summing `loss.item()`, stayed at 12.00 GiB for all twelve batches (Figure 7).

PyTorch's FAQ opens its out-of-memory advice with this habit, warning that `total_loss += loss` in a training loop accumulates history, fixed with `float(loss)`. <!-- L31 --> The lab measured that case too: with `running_loss += loss` after each `backward()`, allocated memory at the end of both training steps was identical to the byte. `backward()` had already freed what each step saved, so the graph that remains costs host memory, not GPU memory. The expensive version is a loop that never calls `backward()`.

To catch a retained graph, read `torch.cuda.memory_allocated()` at the same point of two consecutive iterations, not just the first two. Adam creates its state on its first `step()`, so here allocated memory rose 8 GiB between steps 0 and 1 without any leak.

## Who else is holding the card?

The `Process N` lines come from NVML's list of *compute* processes: those with a CUDA context. Graphics applications, such as an X server or a browser drawing with the GPU, are not on that list. <!-- L34 --> On this GB10, which drives a desktop, five graphics processes held 792 MiB — Xorg 250 MiB, Firefox 279 MiB — and none of them would appear in an out-of-memory message. On a discrete card, total minus free minus every listed process is memory the message cannot attribute; that unnamed remainder is where they show up.

The leftover process is usually called a zombie, and the word is wrong in a way that matters. When a process ends, the kernel closes all its file descriptors; <!-- L38 --> a Unix zombie is a process that has ended but whose parent has not yet collected its exit status, and the kernel keeps only its PID, status and resource usage. <!-- L39 --> The lab made one: a child allocated 6 GiB and exited, and its parent did not reap it. It was a zombie 0.27 s later, and 0.13 s after that its 6 GiB was back while it was still a zombie. What actually holds memory is a process that is still alive — an orphan whose parent died, adopted by `init` or a subreaper, <!-- L38 --> like run 4's holder: parent PID 1, state sleeping, 6.17 GiB. Take the PID from the message to `ps -o pid,ppid,stat,etime,cmd -p <pid>`; a parent of 1 and an old start time give it away.

Memory outside PyTorch in your own process is the other half of the ledger PyTorch does not keep. The message gives it as *this process* minus allocated minus unallocated. Memory snapshots cannot see it: they record only PyTorch's allocator, not memory from raw CUDA calls, from cuda-python or from NCCL, the collective-communication library. <!-- L27 --> The lab measured what one process holds outside PyTorch as it starts using the GPU (Figure 8):

![Memory one process holds outside PyTorch: a 173 MiB context with lazy loading, 943 MiB eager, and 892 MiB with NCCL on one rank](FIG_08)
*Figure 8. The CUDA context is the floor, and lazy loading keeps it small. A communication library started on a single rank took more than the context and the kernels together.*

The **CUDA context** is the driver's per-process state on the device, including the code of every kernel it has loaded. Since CUDA 12.2 on Linux, kernels load lazily, on first use, which defers their memory until then; `CUDA_MODULE_LOADING=EAGER` restores the old behaviour. <!-- L32 --> On this GB10 the eager context was 943 MiB against 173 MiB lazy. Lazy loading has a catch: a kernel's memory is taken when it first runs, so a process that has already handed every byte to a cache can fail later just loading a kernel. <!-- L33 --> Starting NCCL's communicator, even for one rank, added 548 MiB, and destroying it gave back 388 MiB. One correction to common advice: at 2.15.0 cuBLAS's workspace is no longer outside PyTorch's books. PyTorch takes it from its own allocator for each operation and returns it afterwards — 32 MiB per operation on compute capability 9.x to 12.x — so it counts as allocated. <!-- L30 -->

Run 5's 4 GiB pool stands for the case that bites hardest: a second library that manages its own memory, such as a data-loading or preprocessing library with its own pool, or a second framework. The fix is to free or shrink that pool before training, or to route its allocations through PyTorch's allocator if it offers that. PyTorch's documentation suggests comparing `torch.cuda.device_memory_used()`, NVML's device-wide figure read through the `nvidia-ml-py` package, with its own numbers; <!-- L28 --> the message's *this process* line is more precise, because device-wide usage includes everyone else.

## What changes when GPU memory is system memory?

The GB10 is an integrated GPU: its memory is the operating system's memory, and that changes three readings. CUDA's total, 121.63 GiB, is exactly the kernel's `MemTotal`. CUDA's free was 104.25 GiB, equal to `MemFree` to the hundredth of a GiB, while `MemAvailable` said 114.45: memory Linux could reclaim, 9.18 GiB of it page cache, does not count as free to CUDA. NVIDIA's guidance for these systems says the same — `cudaMemGetInfo` does not count reclaimable memory and can report less than an application could allocate — and tells developers to read `/proc/meminfo` too. <!-- L37 -->

![On the GB10, CUDA free and MemFree fall together from 104.25 to 96.22 GiB under an 8 GiB CPU tensor; MemAvailable stays higher](FIG_09)
*Figure 9. On a GPU that shares memory with the CPU, an ordinary CPU allocation shrinks what CUDA calls free, and no GPU process is charged for it.*

Figure 9 is cause 4 with a twist. An 8 GiB CPU tensor in an ordinary Python process cut CUDA's free memory by 8.02 GiB, and NVML charged it to no GPU process. On a unified-memory machine, *another process* includes every program on the computer, and it appears in the message only as unattributed memory. `nvidia-smi` shows `Memory-Usage: Not Supported` there by design, while still listing per-process memory, <!-- L36 --> and `torch.cuda.device_memory_used()` raised `NVMLError_NotSupported` on this machine. On Tegra-class devices such as Jetson, the per-process lines can be missing from the message altogether. <!-- L17 -->

## The math: the ledger in symbols

| Symbol | Meaning |
|---|---|
| $C$ | capacity of the card |
| $R$ | the request, `Tried to allocate` |
| $F$ | free memory on the card |
| $Y$ | this process, including non-PyTorch memory |
| $O$ | the sum of the listed other processes |
| $X$ | memory no listed process accounts for |
| $A$, $U$ | allocated by PyTorch; reserved but unallocated |
| $N$ | this process's memory outside PyTorch |
| $g$ | growth of allocated memory between two iterations |
| $B$ | the batch size, in rows |

On a discrete card, everything that is not free belongs to someone:

$$
C = F + Y + O + X, \qquad Y = A + U + N.
$$

The first identity says the card is fully accounted for, and the second splits this process into PyTorch's books and the rest. The request fails when no free block of $R$ exists and the card cannot supply a new one, so the shortfall is

$$
D = R - F .
$$

Each cause is the one holder whose excess alone would have covered the shortfall, tested in the order of Figure 3: a retained graph if $g \gt 0$; fragmentation if $U \geq R$; another process if $O + \max(X - b, 0) \geq D$; memory outside PyTorch if $N - b \geq D$, where $b$ is a normal floor of about half a GiB for the CUDA context, and the larger excess wins when both hold; capacity otherwise.

Run 4 collapses back to numbers. On the 24 GiB card, $C = 24.00$, $Y = 17.83$ and $O = 6.17$, so $F = 0.00$ and $D = 0.25$ GiB. $U$ is 2 MiB, far below $R$, and $O = 6.17 \geq D$: another process. Capacity has a formula of its own for this model. It has $P = 2^{30}$ parameters. Once Adam's state exists, the forward pass holds 12 bytes for each of them — the weight and its two averages, the gradients having been freed — and every row of the batch saves two 32 KiB rows per layer, plus one row each for the input and the output:

$$
M_{\text{forward}} \approx 12\ \text{GiB} + B \times 1.0625\ \text{MiB},
$$

which is 18.38 GiB at $B = 6{,}144$ and 24.75 GiB at $B = 12{,}288$. In words: once the optimizer state exists, every row of the batch costs a little over a mebibyte of activations.

## Implementation: reading the message in code

The evidence has to be collected while the process is alive. A training step can keep the one number the message cannot give, growth, and save the rest when it fails:

```python
import torch

torch.cuda.memory._record_memory_history(max_entries=200_000)  # for the snapshot, before training

def run_step(step_fn, step, history):
    history.append(torch.cuda.memory_allocated())  # same point every iteration: the growth signal
    try:
        step_fn()
    except torch.OutOfMemoryError as err:
        stats = torch.cuda.memory_stats()
        print(err)  # the six numbers
        print("step", step, "allocated at step starts (GiB):", [round(a / 2**30, 2) for a in history[-4:]])
        print("cache flushes:", stats["num_alloc_retries"],
              "free inside split blocks (GiB):", stats["inactive_split_bytes.all.current"] / 2**30)
        torch.cuda.memory._dump_snapshot("oom-snapshot.pickle")  # open in pytorch.org/memory_viz
        raise
```

Recording history adds a stack trace to every allocation event, so turn it on to reproduce a failure rather than in every run. The snapshot opens in `pytorch.org/memory_viz`, where Figure 5's tails appear as gaps between blocks. <!-- L27 --> `inactive_split_bytes` is the allocator's own count of free space inside split blocks, which matched run 1's 4.63 GiB.

The lab's `diagnose.py` applies Figure 3's tree to a message using the standard library only:

```bash
python diagnose.py --message-file oom.txt --growth 1.55GiB
```

It prints the cause, the number that decided it and the usual fix. On the lab's own captures it reproduces all five verdicts on a machine with no GPU; the files are under [Lab downloads](#lab-downloads).

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** catching the error and calling `torch.cuda.empty_cache()` before retrying. The allocator already released every cached segment it could before it raised; the lab's two retries failed again with the same request.

- **The card was emulated.** On a real 24 GiB card the driver refuses `cudaMalloc` instead of the "allowed" check, the message has no "allowed" clause, and total and free describe the card. The meaning of every other number is unchanged.
- **Treating every error as capacity.** Halving the batch makes a retained graph fail later; it does not fix it, and it hides fragmentation that came from a shape change.
- **Reading `nvidia-smi` after the crash.** The process has exited and released its memory; read the message, or keep the snapshot.
- **Setting both allocator variables.** `PYTORCH_CUDA_ALLOC_CONF` wins at 2.15.0 whatever the documentation implies. <!-- L24 -->
- **CUDA graphs.** Memory captured into a graph lives in a private pool, which the message reports separately, and the allocator does not release cached memory while a capture is under way, so an error during capture can be caused by the cache itself. <!-- L15 --> <!-- L16 -->
- **Unified memory.** On a GB10 or a DGX Spark, free memory moves with every program on the machine and excludes the page cache; Figure 9's section applies.
- **This post does not size a deployment.** How much memory a serving engine needs for a model and its cache is for later in this series.

## Key takeaways

- **The message is a ledger of six numbers from three instruments.** The first line is the same for every cause; the cause is in the last four.
- **Check growth first.** A leak eats the headroom until a small request fails among slivers, so its message also reads as fragmentation.
- **Reserved but unallocated at least the request means fragmentation.** Turn on expandable segments with the variable the code reads, or keep shapes stable.
- **Bytes outside PyTorch need a fix outside PyTorch.** Look for the PID in the message (a live orphan, not a zombie) or for *this process* minus PyTorch's reserved memory: the context, NCCL, a library's pool.
- **`empty_cache()` cannot rescue the process that crashed.** It only helps other processes.

## Try it yourself

<details><summary>Run 1 doubled the batch to 12,288 rows. At 10,240 rows, how large would each activation be, how large the tail beside each 256 MiB tensor, and could any tail hold a 256 MiB request?</summary>

Each activation would be 10,240 × 8,192 × 4 bytes = 320 MiB. Best fit would put a 256 MiB tensor in each freed 320 MiB block and leave a 64 MiB tail, which can never hold a 256 MiB request. Whether the run fails depends on how many tails form before the card fills, which only running it can say; if it fails, reserved but unallocated will again be many times the request.

</details>

<details><summary>Run 5's message reads: this process has 23.83 GiB in use; 19.67 GiB allowed; 19.50 GiB allocated by PyTorch; 2.00 MiB reserved but unallocated. What holds the missing memory, and how much?</summary>

Something in this process outside PyTorch: 23.83 − (19.50 + 0.002) ≈ 4.33 GiB. That is the 4 GiB library pool plus the 0.33 GiB CUDA context. Fragmentation is ruled out because 2 MiB is far below the 256 MiB request, and no other process is listed.

</details>

<details><summary>Using the formula in the math section, what is the largest batch whose forward pass fits in step 1 on the 24 GiB card, where 23.67 GiB is allowed?</summary>

12 GiB + B × 1.0625 MiB ≤ 23.67 GiB gives B ≤ 11.67 × 1,024 / 1.0625 ≈ 11,250 rows. That ignores fragmentation and the optimizer step, whose 20.00 GiB peak does not depend on the batch.

</details>

The lab's exercise ladder goes further: E1 reproduces the five verdicts from the capture with no GPU, and E4 gives you an unnamed fault on a real one. Both are under [Lab downloads](#lab-downloads).

## References

### Lab downloads

- [`README.md`](LAB_01) — grade, what was executed, the provenance line, run order, the exercise ladder and cleanup.
- [`oom_lab.py`](LAB_02) — needs one NVIDIA GPU: runs the baseline, the five failures, their fixes and the measurements on an emulated 24 GiB card, each in a fresh process.
- [`diagnose.py`](LAB_03) — runs anywhere: applies the decision tree to a message or to a captures file.
- [`captures.json`](LAB_04) — the run this article quotes: every message, ledger, allocator snapshot summary and trace.
- [`expected-output.txt`](LAB_05) — the console output of that run.
- [`requirements.txt`](LAB_06) — the pinned versions the run used.
- [`notebook.ipynb`](LAB_07) — the README with a runnable cell under each step and exercise.
- [Complete lab](https://minio.canery.in/media/lab-five-causes-of-cuda-out-of-memory.zip) — every file above in one zip.

### Sources

**Literature**

- Y. Tang, L. Qiao, L. Yin, P. Liang, A. Shen, Z. Yang, "Training large-scale language models with limited GPU memory: a survey", *Frontiers of Information Technology & Electronic Engineering*, 2025. [https://doi.org/10.1631/fitee.2300710](https://doi.org/10.1631/fitee.2300710)
- P. R. Wilson, M. S. Johnstone, M. Neely, D. Boles, "Dynamic Storage Allocation: A Survey and Critical Review", IWMM 1995, LNCS 986. [https://doi.org/10.1007/3-540-60368-9_19](https://doi.org/10.1007/3-540-60368-9_19)
- M. S. Johnstone, P. R. Wilson, "The Memory Fragmentation Problem: Solved?", ISMM 1998. [https://doi.org/10.1145/286860.286864](https://doi.org/10.1145/286860.286864)
- A. Paszke et al., "PyTorch: An Imperative Style, High-Performance Deep Learning Library", NeurIPS 2019. [https://arxiv.org/abs/1912.01703](https://arxiv.org/abs/1912.01703)
- S. Rajbhandari, J. Rasley, O. Ruwase, Y. He, "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", SC20. [https://doi.org/10.1109/SC41405.2020.00024](https://doi.org/10.1109/SC41405.2020.00024)
- Y. Zhao et al., "PyTorch FSDP: Experiences on Scaling Fully Sharded Data Parallel", PVLDB 16(12), 2023. [https://doi.org/10.14778/3611540.3611569](https://doi.org/10.14778/3611540.3611569)
- C. Guo et al., "GMLake: Efficient and Transparent GPU Memory Defragmentation for Large-scale DNN Training with Virtual Memory Stitching", ASPLOS 2024. [https://doi.org/10.1145/3620665.3640423](https://doi.org/10.1145/3620665.3640423)
- R. Zhang, W. Xiao, H. Zhang, Y. Liu, H. Lin, M. Yang, "An Empirical Study on Program Failures of Deep Learning Jobs", ICSE 2020. [https://doi.org/10.1145/3377811.3380362](https://doi.org/10.1145/3377811.3380362)
- T. Chen, B. Xu, C. Zhang, C. Guestrin, "Training Deep Nets with Sublinear Memory Cost", arXiv preprint, 2016. [https://arxiv.org/abs/1604.06174](https://arxiv.org/abs/1604.06174)

**PyTorch documentation, source and history (2.15.0)**

- *CUDA semantics*: memory management, `PYTORCH_ALLOC_CONF` options, cuBLAS workspaces. [https://docs.pytorch.org/docs/stable/notes/cuda.html](https://docs.pytorch.org/docs/stable/notes/cuda.html) (accessed 2026-10-30)
- *Understanding CUDA Memory Usage*: snapshots and non-PyTorch allocations. [https://docs.pytorch.org/docs/stable/torch_cuda_memory.html](https://docs.pytorch.org/docs/stable/torch_cuda_memory.html) (accessed 2026-10-30)
- *Frequently Asked Questions*: out of memory. [https://docs.pytorch.org/docs/stable/notes/faq.html](https://docs.pytorch.org/docs/stable/notes/faq.html) (accessed 2026-10-30)
- *torch.optim*: algorithms and their default implementations. [https://docs.pytorch.org/docs/stable/optim.html](https://docs.pytorch.org/docs/stable/optim.html) (accessed 2026-10-30)
- `c10/cuda/CUDACachingAllocator.cpp` at tag v2.15.0. [https://github.com/pytorch/pytorch/blob/v2.15.0/c10/cuda/CUDACachingAllocator.cpp](https://github.com/pytorch/pytorch/blob/v2.15.0/c10/cuda/CUDACachingAllocator.cpp)
- `c10/core/AllocatorConfig.h` and `c10/cuda/CUDAAllocatorConfig.h` at tag v2.15.0. [https://github.com/pytorch/pytorch/blob/v2.15.0/c10/core/AllocatorConfig.h](https://github.com/pytorch/pytorch/blob/v2.15.0/c10/core/AllocatorConfig.h)
- `aten/src/ATen/cuda/CublasHandlePool.cpp` at tag v2.15.0. [https://github.com/pytorch/pytorch/blob/v2.15.0/aten/src/ATen/cuda/CublasHandlePool.cpp](https://github.com/pytorch/pytorch/blob/v2.15.0/aten/src/ATen/cuda/CublasHandlePool.cpp)
- `torch/cuda/__init__.py` and `torch/cuda/memory.py` at tag v2.15.0. [https://github.com/pytorch/pytorch/blob/v2.15.0/torch/cuda/__init__.py](https://github.com/pytorch/pytorch/blob/v2.15.0/torch/cuda/__init__.py)
- Pull requests #96995, #99093, #113481 and #130959. [https://github.com/pytorch/pytorch/pull/113481](https://github.com/pytorch/pytorch/pull/113481) (accessed 2026-10-30)
- E. Yang, "When does fragmentation occur in the CUDA caching allocator?", PyTorch devlog, 2026-06-01. [https://docs.pytorch.org/devlogs/eager/2026-06-01-cuda-caching-allocator/](https://docs.pytorch.org/devlogs/eager/2026-06-01-cuda-caching-allocator/) (accessed 2026-10-30)
- `torch` release metadata on PyPI. [https://pypi.org/pypi/torch/json](https://pypi.org/pypi/torch/json) (accessed 2026-10-30)

**NVIDIA documentation**

- CUDA Programming Guide v13.4.2, §4.7 *Lazy Loading*. [https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/lazy-loading.html](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/lazy-loading.html) (accessed 2026-10-30)
- CUDA Driver API v13.4, *Virtual Memory Management*. [https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__VA.html](https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__VA.html) (accessed 2026-10-30)
- NVML `nvmlDeviceGetComputeRunningProcesses_v3`, in the cuda-python documentation. [https://nvidia.github.io/cuda-python/cuda-bindings/latest/module/generated/cuda.bindings.nvml.device_get_compute_running_processes_v3.html](https://nvidia.github.io/cuda-python/cuda-bindings/latest/module/generated/cuda.bindings.nvml.device_get_compute_running_processes_v3.html) (accessed 2026-10-30)
- DGX Spark User Guide, *Known Issues*. [https://docs.nvidia.com/dgx/dgx-spark/known-issues.html](https://docs.nvidia.com/dgx/dgx-spark/known-issues.html) (accessed 2026-10-30)

**Linux**

- `_exit(2)`, Linux man-pages 6.18. [https://man7.org/linux/man-pages/man2/_exit.2.html](https://man7.org/linux/man-pages/man2/_exit.2.html) (accessed 2026-10-30)
- `wait(2)`, Linux man-pages 6.19. [https://man7.org/linux/man-pages/man2/wait.2.html](https://man7.org/linux/man-pages/man2/wait.2.html) (accessed 2026-10-30)
