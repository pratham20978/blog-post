---
title: "Why Your GPU Is Idle at 100% Utilization"
slug: "gpu-idle-at-100-percent-utilization"
date: 2026-09-24
updated: 2026-09-24
summary: "nvidia-smi's 100% means some kernel was running, not that the GPU was busy. Where a slow step's time really goes: launch queues, sync points and launch overhead."
tags: [machine-learning, cuda, nvidia, gpu, performance, pytorch, cuda-graphs]
category: "machine-learning"
series: nvidia-stack
series_position: 3
tier: L3
difficulty: intermediate
prerequisites: ["python", "what a thread is", "the NVIDIA layer map"]
reading_minutes: 31
cover_image: "https://minio.canery.in/media/cover-gpu-idle-at-100-percent-utilization.png"
canonical_url: "https://canery.in/blogs/gpu-idle-at-100-percent-utilization"
---
> [!NOTE]
> **Insights** — `nvidia-smi`'s GPU utilization is the share of a sample window, between 1/6 s and 1 s long, during which at least one kernel was executing. It has no term for how much of the chip that kernel used, so a single thread spinning in one block reads 100% while every other streaming multiprocessor sits empty. When a job is slow, the missing time is usually on the host: kernel launches are asynchronous, a line like `loss.item()` drains the queue, and a Python timer bills the wait to that line instead of the work that caused it. Time the GPU with CUDA events, find the sync points, and count the launches before you blame the kernels.

**Level:** intermediate · **You need:** Python, what a thread is, and [part 1&#39;s layer map](https://canery.in/blogs/what-the-nvidia-stack-actually-is#the-problem-five-different-things-are-called-cuda) · **Time:** ~31 min

> [!TIP]
> **Two labs, two hardware tiers.** The worked example comes from a small model of one CUDA stream that runs on any machine with Python and needs no GPU — every number in the example, the figures and the lab is printed by the same script. A second pair of scripts measures the real values on one NVIDIA GPU; they ship with an empty results file, because the machine this was written on has no NVIDIA GPU and nothing here is invented. Both are under [Lab downloads](#lab-downloads).

## Why this matters

The dashboard says the GPU is at 97%. The training step takes twice as long as the arithmetic says it should. Both statements are true, and the usual response — a bigger GPU, or a week spent on kernel tuning — treats the first as evidence about the second. It is not.

Microsoft studied 400 deep-learning jobs on its internal platform that averaged 50% GPU utilization or less, and found 706 separate causes. The largest categories were host-to-GPU data transfer (27.9%), a batch size too small for the device (25.6%) and synchronous checkpointing (16.4%); 84.99% of the issues were fixable with small code or script changes.   None of the three largest was a slow kernel. And the number misleads in the other direction too: one profiling study watched `nvidia-smi` report 100% while each of sixteen worker processes spent about 20 seconds of a run lasting up to 5,080 seconds actually executing GPU kernels. 

[Part 1](https://canery.in/blogs/what-the-nvidia-stack-actually-is#the-problem-five-different-things-are-called-cuda) traced one tensor operation down through the framework, the CUDA runtime, the user-mode driver and the kernel module. This part follows what happens to *time* on that path — which is a question about queues, not layers.

## The problem: a clock, not a gauge

`nvidia-smi` defines GPU utilization as the percentage of the last sample period during which one or more kernels — functions running on the GPU — was executing.  The sample period is between 1/6 of a second and one second, depending on the product.  The same definition sits behind the `nvmlUtilization_t.gpu` field of NVML, the NVIDIA Management Library: the library `nvidia-smi` is built on, and the one monitoring agents read. 

Read that definition twice, because of what it leaves out. It is a fraction of *time*. It says nothing about *space*.

The space is made of streaming multiprocessors. A **streaming multiprocessor (SM)** is the GPU's unit of parallel execution: a kernel is launched as a grid of thread blocks, and the hardware spreads those blocks across the SMs. A kernel with fewer blocks than the chip has SMs leaves the rest idle for as long as it runs. That is the quantity the utilization number cannot see.

NVIDIA ships a metric that can. DCGM, the Data Center GPU Manager, reports **SM Activity**: the fraction of time at least one warp — the group of threads an SM schedules as one unit — was active on an SM, averaged over all SMs.  Its documentation even works the example. On a GPU with N SMs, a kernel with N blocks running for the whole interval scores 1.0; a kernel with N/5 blocks for the whole interval scores 0.2; a kernel with N blocks for one fifth of the interval also scores 0.2.  Put those workloads next to `nvidia-smi`'s definition and the problem draws itself.

![Four panels, each a grid of SMs against time within one sample window, with the nvidia-smi utilization and DCGM SM Activity each workload would read](https://minio.canery.in/media/fig-01-clock-not-gauge-gpu-idle-at-100-percent-utilization.png)

*Figure 1. Panels A and B read 100% utilization on a chip that is at least four-fifths empty. Only D is the machine the number suggests.*

Panel A is not hypothetical. PyTorch ships a private helper, `torch.cuda._sleep`, that launches exactly that: a grid of one block of one thread that busy-waits for a set number of clock cycles.  By NVIDIA's definition it holds utilization at 100% for as long as it spins. DCGM's own guidance puts the bar for effective use at an SM Activity of 0.8 or more, and calls anything below 0.5 likely ineffective.  A 2025 systems paper states the limitation flatly: the utilization metric shows the share of time some kernel is active and reveals nothing about how well the kernels use the GPU. 

There is a second, messier problem: in practice the counter may not even behave like the time fraction it is documented as. RL-Scope's 100% reading from the opening came from a GPU that was executing kernels for a small fraction of the time.  The authors of the Microsoft Philly trace study went further: they warn that the counter on their GPUs could only detect whether *any* SM was in use, and treat every figure they report as an upper bound.  NVIDIA's documentation does not describe how the sample is taken, so which reading holds on a given GPU is something to measure, and one of the lab scripts does.

So the number has two blind spots. It cannot see space at all, and it is a coarse view of time. When a job is slow and the dashboard is high, it has told you nothing you can act on. What you need is the answer to a more specific question: *where did this step's milliseconds go?* Answering it takes two clocks.

## Worked example: one training step, timed twice

Here is an ordinary training loop. It logs the loss every step, a habit that costs more than it looks.

```python
for x, y in loader:
    out = model(x)                 # forward
    loss = loss_fn(out, y)
    loss.backward()                # backward
    losses.append(loss.item())     # logging
    opt.step()                     # optimizer
    opt.zero_grad()
```

The **host** here is the CPU thread running that Python: it issues work to the GPU and moves on. To make the arithmetic followable by hand, give each phase round numbers. These are the inputs of a model, not a measurement — the lab's model script reproduces every number below, and a second script measures the real ones on a GPU.

| Phase           | Kernels launched | Host time per launch | GPU time per kernel |
| --------------- | ---------------- | -------------------- | ------------------- |
| forward         | 40               | 20 µs               | 100 µs             |
| backward        | 80               | 20 µs               | 100 µs             |
| `loss.item()` | none — it waits | —                   | —                  |
| optimizer       | 1,000            | 20 µs               | 3 µs               |

The 20 µs is the host's cost to issue one operator. The CUDA launch itself is only part of it — NVIDIA's measurement later in this post puts launch and synchronisation overhead at a few microseconds per kernel on a V100  — and a framework adds its own work before every launch: choosing the operator, checking types and shapes, computing the output shape, picking a kernel, allocating memory, packing arguments.  The optimizer is written as a for-loop over 100 parameter tensors, each needing 10 small element-wise kernels: the implementation PyTorch documents as slower than its *foreach* and *fused* variants precisely because it makes many sequential kernel calls. 

### Timing it the obvious way

Wrap each phase in `time.perf_counter()`, the host's clock:

| Phase           | Host timer        |
| --------------- | ----------------- |
| forward         | 0.8 ms            |
| backward        | 1.6 ms            |
| `loss.item()` | **9.6 ms**  |
| optimizer       | 20.0 ms           |
| **step**  | **32.0 ms** |

The verdict writes itself: logging costs nearly a third of the step, and backward is cheap. Both halves of that verdict are wrong, and the reason is in how the first line executes.

A **kernel launch** is the host call that places one GPU function in a queue. It is asynchronous: the call returns without waiting for the kernel to finish, or even to start.  PyTorch is built on this — every GPU operation merely enqueues work that may execute later.  So `model(x)` returns after 40 launches × 20 µs = **0.8 ms**, having queued 4.0 ms of kernels. `loss.backward()` returns after 80 × 20 µs = **1.6 ms**, having queued another 8.0 ms. The host is now at 2.4 ms. The GPU, which started the first forward kernel almost immediately, has finished about 2.4 ms of its 12.0 ms backlog.

Then `loss.item()` asks for a number that lives on the GPU. A **synchronization point** is any call that blocks the host until queued GPU work has finished, and copying a value back to the host is one: the copy cannot complete until every kernel ahead of it in the queue has.   The host waits until the GPU reaches 12.0 ms, which is 12.0 − 2.4 = **9.6 ms**. The logging line did no work in that time. It stood in line.

Finally the optimizer issues 1,000 launches at 20 µs each: **20.0 ms**. Each kernel takes 3 µs, so the GPU finishes it and then waits 17 µs for the next to arrive. Figure 2 draws the whole step on two lanes, one per clock.

![The host lane and GPU lane of the step drawn to one time scale, showing the host blocked in loss.item() while the GPU runs backward, then the GPU mostly idle while the host issues the optimizer](https://minio.canery.in/media/fig-02-one-step-two-lanes-gpu-idle-at-100-percent-utilization.png)

*Figure 2. Before 12 ms the host is ahead and waiting; after it, the GPU is ahead and waiting. Model inputs, not a measurement.*

### Timing it on the GPU's clock

A **CUDA event** is a marker placed in the queue. Recording one is itself an asynchronous call that returns at once, and the GPU stamps the marker with its own clock when it reaches the front of the queue.  PyTorch's documentation is blunt that timings taken without synchronization are wrong, and names events as one of the two correct tools. 

```python
ev = [torch.cuda.Event(enable_timing=True) for _ in range(5)]
ev[0].record(); out = model(x); loss = loss_fn(out, y)
ev[1].record(); loss.backward()
ev[2].record(); losses.append(loss.item())
ev[3].record(); opt.step(); opt.zero_grad()
ev[4].record()
torch.cuda.synchronize()                              # one sync, after the step
print([ev[i].elapsed_time(ev[i + 1]) for i in range(4)])   # milliseconds
```

| Phase           | Host timer        | CUDA events       |
| --------------- | ----------------- | ----------------- |
| forward         | 0.8 ms            | 4.0 ms            |
| backward        | 1.6 ms            | 8.0 ms            |
| `loss.item()` | 9.6 ms            | **0.0 ms**  |
| optimizer       | 20.0 ms           | 20.0 ms           |
| **step**  | **32.0 ms** | **32.0 ms** |

![Paired bars per phase comparing host-timer and CUDA-event readings, with the 9.6 ms billed to loss.item() traced back to forward and backward GPU work](https://minio.canery.in/media/fig-03-two-readouts-gpu-idle-at-100-percent-utilization.png)

*Figure 3. Same total, different story. The host timer's 9.6 ms for `loss.item()` is forward and backward's GPU time, less the 2.4 ms the host spent issuing it.*

Read the two columns together, as Figure 3 does, because the comparison is the diagnosis. Where the events read five times the host timer — forward and backward — the GPU was the bottleneck and the host had run ahead. Where the events read zero, the line did no GPU work; it only waited. Where the two clocks *agree* — the optimizer, 20.0 ms on both — the GPU was waiting on the host for the whole phase, and inside those 20.0 ms the kernels ran for just 3.0.

Add it up. The GPU executes kernels for 15.0 ms of a 32.0 ms step and sits idle for 17.0 ms: **53% of the step, more than half the wall clock, is host-side.** By NVIDIA's definition a window of such steps would read 15.0 / 32.0 = 47% — and if the counter over-reads short kernels the way RL-Scope observed, higher still.

The naive timer did not get the total wrong. It got the *bill* wrong: it charged 9.6 ms to the one line that did no work, and under-charged backward by 6.4 ms. Acting on it — shaving the logging, or the backward pass — attacks the wrong thing.

## Intuition: two clocks and a queue

The host thread and the GPU keep separate clocks, and a queue sits between them. That queue is a **CUDA stream**: a work queue whose operations run in the order they were enqueued, none overtaking another.  The host pushes launches into one end; the GPU takes them off the other.

This is the design, not an accident. PyTorch's authors describe using CUDA streams so that Python code on the CPU overlaps operators executing on the GPU, which is how an interpreted language keeps an accelerator busy.  In their own trace of a ResNet-50 training step, GPU execution took about three times as long as CPU scheduling — the host stayed ahead and the GPU was kept almost fully busy.  Everything goes well as long as the queue has something in it.

The depth of that queue tells you who is waiting for whom, and Figure 4 plots it for the worked example.

![Queue depth over the worked example's step: rising to 97 kernels at 2.4 ms, draining to zero at 12 ms, then never above one](https://minio.canery.in/media/fig-04-queue-depth-gpu-idle-at-100-percent-utilization.png)

*Figure 4. A deep queue means the GPU is the bottleneck. An empty one means the host is. Model output, not a measurement.*

Before 2.4 ms the host adds kernels five times faster than the GPU finishes them, and the queue grows to 97. From 2.4 to 12.0 ms the host is parked in `loss.item()` while the queue drains. After 12.0 ms the queue never holds more than the kernel that is running: each launch arrives at an idle GPU.

That produces the rule this whole post exists to deliver. **A sync point costs almost nothing itself. It costs the overlap it destroys.** Without `loss.item()` in the middle, the optimizer's 20 ms of issuing would have started at 2.4 ms and run *while* the GPU chewed through forward and backward. The sync forced those two things to happen one after the other.

A restaurant's ticket rail is a fair picture. The waiter clips orders to the rail and goes back to the floor; the cook works through them in order. A waiter who stands at the pass until a dish is ready is `loss.item()` — no dish is cooked any faster, but no new orders are taken meanwhile. A waiter who writes tickets more slowly than the cook cooks is a launch-bound optimizer: the cook stands idle between tickets, and the kitchen still counts as open. The analogy breaks on the kitchen itself. A GPU is a kitchen in which one ticket may occupy a single burner or every burner at once — and `nvidia-smi` only ever asks whether *some* ticket is being cooked.

## What is a stream, and what does an event time?

A stream promises order within itself and nothing across streams. Work in two different streams may run concurrently — but only when no event links them, no implicit synchronization intervenes, and the GPU has resources to spare.  That is what lets a copy of the next batch overlap the current batch's compute, as in Figure 5:

![A host lane issuing five calls that each return at once, a copy stream moving the next batch, and a compute stream whose next step waits on an event recorded after the copy](https://minio.canery.in/media/fig-05-two-streams-one-event-gpu-idle-at-100-percent-utilization.png)

*Figure 5. Nothing on the host lane blocks. The order between the two streams lives in event E, on the GPU.*

The copy runs on stream A; an event E is recorded after it; stream B is told to wait on E before the next step reads the batch. `cudaStreamWaitEvent` makes later work in a stream wait for an event, and CUDA resolves that wait on the device where it can, so the host does not block.  For the copy to overlap at all, the host memory must be pinned — page-locked, so the operating system cannot move it — and the copy must be on a non-default stream.  A copy from ordinary pageable memory can be synchronous with the host and overlaps nothing. 

### The default stream is a barrier

Launch without naming a stream and the work goes to the **legacy default stream**, stream 0. It is a blocking stream in a specific sense: it synchronizes with every other blocking stream. Launch k1 on stream 1, then k2 on stream 0, then k3 on stream 2, and CUDA runs them strictly one after another.  Streams created with the `cudaStreamNonBlocking` flag are exempt.  Figure 6 sets the two cases side by side.

![Two panels: three kernels on blocking streams serialised by the default stream, and the same three on non-blocking streams free to overlap](https://minio.canery.in/media/fig-06-default-stream-gpu-idle-at-100-percent-utilization.png)

*Figure 6. Stream 0 is a hidden barrier between streams created the ordinary way.*

PyTorch's default stream is stream 0 — its handle is literally the null stream — and the side streams it hands out from its pool are created non-blocking.  Ordinary single-stream PyTorch code behaves as if every operation were synchronous for a simpler reason: each device runs its queue in order, and PyTorch inserts the synchronization it needs whenever data moves between CPU and GPU.  CUDA also offers a per-thread default stream, enabled with `nvcc --default-stream per-thread`, which does not synchronize with other streams. 

### What an event actually measures

An event's timestamp is taken when the GPU *reaches* it.  The difference between two events is therefore the time the stream took to go from one marker to the other, gaps included. That is why the optimizer read 20.0 ms on the event clock with only 3.0 ms of kernels inside: the stream was waiting for launches, and the events faithfully timed the waiting.

`cudaEventElapsedTime` reports milliseconds with a resolution of about 0.5 µs.  Its documentation adds a caveat that matters as soon as events are recorded outside stream 0: if either event was last recorded on a non-default stream, the measured time may be longer than expected, because other work can run between the two records.  In PyTorch, an event can only be timed if it was created with `enable_timing=True`, and `elapsed_time` returns milliseconds. 

## Host-side sync points

A host-side sync point is any call that stops the host thread until some or all of the GPU's queued work has finished. Some are explicit. `torch.cuda.synchronize()` waits for every kernel in every stream on the device;  at the CUDA level, `cudaDeviceSynchronize` waits for all preceding work in all streams of all host threads, and `cudaStreamSynchronize` for one stream.  Those you wrote, and you can find them.

The ones that hurt are implicit: calls that need a value, a size or a decision that only the GPU has. PyTorch's Performance Tuning Guide names five kinds — printing a CUDA tensor, `.item()`, memory copies such as `.cuda()` and `.cpu()`, `.nonzero()`, and Python control flow that depends on a CUDA result — and gives the reason to avoid them: to let the CPU run ahead and keep the accelerator's queue full.   Figure 7 collects them with the explicit ones.

![A table of calls that block the host, what each waits for, and where it appears in a training loop, with the implicit ones highlighted](https://minio.canery.in/media/fig-07-sync-points-gpu-idle-at-100-percent-utilization.png)

*Figure 7. The shaded rows are the ones nobody writes on purpose: each moves a value, or a decision, from the GPU back to Python.*

The mechanisms differ. A device-to-host copy returns only when it has completed, and a copy from pageable host memory to the device performs a stream synchronization before it starts.  `.nonzero()` returns a tensor whose size depends on the data, and PyTorch cannot allocate it until the GPU has said how big it is; the PyTorch CUDA Graphs team notes that dynamic shapes force CPU-GPU synchronization for exactly this reason.  An ordinary `x.to("cuda")` is a sync point too: `Tensor.to()` always issues an asynchronous copy, and with `non_blocking=False` — the default — PyTorch calls `cudaStreamSynchronize` after every one.  Freeing device memory is the least obvious: `cudaFree` may block until all queued work on all GPUs has finished, which is one reason PyTorch keeps its own caching allocator rather than calling it.  CUDA itself reserves the right to block any API call when an internal resource runs short. 

These patterns show up in production traces. The Microsoft study located iteration boundaries in its utilization data precisely because per-iteration logging and other non-GPU work made utilization drop sharply and then recover. 

### Making PyTorch name them

You do not have to find sync points by reading code. Turn on sync debugging for one step:

```python
torch.cuda.set_sync_debug_mode("warn")   # every synchronizing call now warns, with a stack trace
```

It is labelled experimental, and PyTorch says plainly that not every synchronizing operation triggers it.  A clean run means "none found", not "none exist".

Two side effects are worth knowing before you go looking. First, a thread waiting on the GPU spins rather than sleeps by default whenever there are no more CUDA contexts than logical processors,  so the Python process shows as fully busy in `top` while it does nothing but wait — CPU utilization lies in the same direction as GPU utilization. Second, `CUDA_LAUNCH_BLOCKING=1` forces a synchronization after every launch. It exists to make errors surface at the line that caused them, and NVIDIA is explicit that it is a debugging aid that slows execution.  Timing with it on measures a different program.

## What does a kernel launch cost?

A launch is cheap in absolute terms and expensive in relative ones. A clean measurement of the relative cost is NVIDIA's own, taken on a Tesla V100 with CUDA 10.1: an element-wise kernel over 500,000 floats that runs for 2.9 µs, launched 20 times per step for 1,000 steps, with the wall clock divided by 20,000. 

![Three horizontal bars of per-kernel cost on a V100 — 9.6, 3.8 and 3.4 microseconds — each split into 2.9 microseconds of kernel and the remaining overhead](https://minio.canery.in/media/fig-08-launch-cost-gpu-idle-at-100-percent-utilization.png)

*Figure 8. The same 2.9 µs kernel costs 9.6 µs when each launch waits for the last, and 3.8 µs when launches overlap execution. Measured by NVIDIA on a Tesla V100 with CUDA 10.1.*

Figure 8 shows the result. With a synchronization after every launch, each kernel effectively costs 9.6 µs — 6.7 µs of overhead on 2.9 µs of work. Drop the per-launch sync, so each launch is issued while the previous kernel runs, and the cost falls to 3.8 µs.  Nothing about the kernel changed. The overhead was still there; it was hidden behind execution.

That is the whole rule for launch overhead: **a launch is hidden only behind a kernel that runs longer than the launch takes.** Large batches make kernels long, so the host stays ahead. Small batches and small models make them short, and the host becomes the critical path. Nimble, a NeurIPS 2020 study, measured PyTorch leaving a V100 idle for up to 91% of the running time in batch-size-1 inference.  In training the same authors found only marginal gains at ImageNet and BERT batch sizes but up to 3.61× on small CIFAR-10 inputs, because large batches hide the scheduling overhead.  A published DALLE2 inference trace at batch size 1 has the worked example's exact shape: over 740 kernels totalling 3.4 ms of GPU time inside a segment that takes 14 ms end to end, about 75% of it attributed to CPU launch delays. 

The cheapest fix does not need anything exotic. The worked example's optimizer made 1,000 launches because it was written as a for-loop; PyTorch's *foreach* implementations combine parameters into multi-tensors and save those sequential kernel calls, *fused* ones go further, and foreach is already the default where it applies.  Fewer, larger launches is the first thing to try.

## What do CUDA Graphs remove, and what do they not?

A **CUDA graph** is a set of GPU operations joined by dependencies and defined separately from its execution. Work is submitted in three stages — definition, instantiation, and execution — and the executable graph can then be launched any number of times.  NVIDIA's stated motivation is the one this post has been circling: every kernel placed in a stream costs host-side setup that can be a significant fraction of a short kernel's time, while a graph pays that setup once, at instantiation.  PyTorch builds graphs by **stream capture**: it puts a stream in capture mode, runs the step once so that the work is recorded into a graph instead of executing, then replays the recording.  `torch.compile(mode="reduce-overhead")` does the capture for you. 

![The worked example's step without its mid-step sync, drawn eager and as one graph replay, with the removed and surviving costs listed](https://minio.canery.in/media/fig-09-what-graphs-remove-gpu-idle-at-100-percent-utilization.png)

*Figure 9. A graph shortens the host lane. It cannot shorten the GPU lane. Model inputs, not a measurement.*

**What a graph removes.** The PyTorch team describes replay as skipping argument setup and kernel dispatch across Python, C++ and the CUDA driver, with that CPU overhead as the main benefit.  In NVIDIA's V100 test, graphing the 20 launches cut the per-kernel cost from 3.8 µs to 3.4 µs.  On Ampere and later GPUs with CUDA 12.6, re-launching a straight-line graph — one whose nodes form a single chain — of ten or more nodes costs the CPU a nearly constant 2.5 µs plus about 1 ns per node, down from 2 µs plus 200 ns per node in CUDA 11.8.  The results follow the regime: in the MLPerf Training v1.0 benchmark, graphs made NVIDIA's PyTorch submissions 1.70× faster for Mask R-CNN and 1.12× faster for BERT,  and turning cudagraphs off lowers the training speedup of TorchInductor, `torch.compile`'s default compiler, from 1.45× over eager to 1.37×.  

**What a graph does not remove.** Every kernel's execution time — in Figure 9 the GPU lane is 15.0 ms before and after. Sync points: an operation that synchronizes the CPU with the GPU, such as `.item()`, is prohibited during capture,  and CUDA treats synchronizing or querying a capturing stream as invalid and discards the whole capture.  So the mid-step `loss.item()` must be removed *before* the step can be graphed at all; the graph does not fix it, it forbids it. CPU work inside the captured region is not recorded and is silently skipped at replay. Dynamic shapes are prohibited, and allocations come from a graph-private memory pool. 

**What a graph adds.** Instantiation cost — about 400 µs in NVIDIA's test, with the first launch about a third slower than later ones.  Memory and re-recording: `reduce-overhead` records a new graph for each input shape and can use more memory.  Changing a graph's topology means re-instantiating it; only node parameters can be updated in place.  For models with dynamic inputs, one study measured placeholder copies costing up to 34% of execution time, per-shape graphs of 20–100 MB each, and control flow such as beam search that could not be captured at all.  Another found that 29 of 116 graphs taken from TorchBench made performance *worse*, mostly from copying kernel parameters into static placeholders.  And a graph has to be replayed enough times to pay for itself: batching iterative kernels into graphs, one study found the graph version overtook plain launches only after two to three batches, with the best batch around 50–100 kernels.  CUDA itself has been moving control flow into graphs — device-side graph launch arrived in CUDA 12.0, IF and WHILE conditional nodes in 12.3, SWITCH in 12.8  — but none of that removes a Python-side `if` on a GPU value.

PyTorch's own advice is the right filter: try graphs when the network is graph-safe and at least somewhat CPU-limited.  The order of operations follows from Figure 9. Remove sync points first: graphs require it anyway, and it is often the cheapest change. Cut launches second, with foreach or fused implementations. Graph what is left.

## The math: a sync point turns one max into a sum

The worked example's timings follow from two lines. Write the step as a sequence of kernels $i = 1, 2, \dots$ issued into one stream.

| Symbol  | Meaning                                      | Units |
| ------- | -------------------------------------------- | ----- |
| $c_i$ | host time to issue kernel$i$               | ms    |
| $d_i$ | GPU time to execute kernel$i$              | ms    |
| $h_i$ | host clock when kernel$i$ enters the queue | ms    |
| $g_i$ | GPU clock when kernel$i$ finishes          | ms    |

$$
h_i = h_{i-1} + c_i, \qquad g_i = \max\left(h_i,\; g_{i-1}\right) + d_i \tag{1}
$$

The host's clock only ever adds issuing costs, and a kernel starts when it has both arrived and the kernel before it has finished. That `max` is the queue.

$$
h \leftarrow \max\left(h,\; g\right) \tag{2}
$$

A sync point moves the host's clock forward to the GPU's. It is the only place the two clocks are forced to agree.

Two cases of equation (1) are worth knowing by heart. If every kernel in a run is host-bound, $c_i \ge d_i$, the GPU finishes each one before the next arrives and the run takes $C = \sum c_i$. If every kernel is GPU-bound, $d_i \ge c_i$, the queue never empties and the run takes $D = \sum d_i$. Either way a uniform run takes $\max(C, D)$ to within one kernel. A loop with no sync points settles to the same per-step period, because the queue carries work across step boundaries and whichever side is slower sets the pace. A sync point stops that carrying. It splits the step into segments that are each maxed separately:

$$
T_{\text{sync}} \approx \max(C_A, D_A) + \max(C_B, D_B) \;\ge\; \max(C_A + C_B,\; D_A + D_B) \approx T_{\text{no sync}} \tag{3}
$$

Here $A$ and $B$ are the segments before and after the sync, each assumed uniform. The sum of the maxes is never smaller than the max of the sums, and that gap is the cost of a sync point. It is zero only when both segments are bottlenecked on the same side.

Now put the worked example back in. Segment A is forward plus backward: $C_A = 2.4$ ms, $D_A = 12.0$ ms, so it takes 12.0. Segment B is the optimizer: $C_B = 20.0$, $D_B = 3.0$, so it takes 20.0. With `loss.item()` between them the step is 12.0 + 20.0 = **32.0 ms**, which is what both clocks measured. Delete the sync, and in a running loop the step settles to $\max(22.4,\ 15.0) =$ **22.4 ms**. Issue the optimizer as 10 launches instead of 1,000, so $C_B = 0.2$, and it becomes $\max(2.6,\ 15.0) =$ **15.0 ms**.

![Three versions of the step drawn to one scale — 32.0 ms, 22.4 ms and 15.0 ms — with utilization by nvidia-smi's definition of 47%, 67% and 100%](https://minio.canery.in/media/fig-10-three-versions-gpu-idle-at-100-percent-utilization.png)

*Figure 10. The last row reads 100%. That is where `nvidia-smi` stops being able to tell you anything. Model inputs, not a measurement.*

Figure 10 draws all three. Utilization by NVIDIA's definition is $U = D / T$ over a window of whole steps: 15.0 / 32.0 = 47%, then 15.0 / 22.4 = 67%, then 15.0 / 15.0 = 100%. The last version is the one a dashboard would call healthy. It is also the version in which every remaining millisecond is inside a kernel — so whether those 15.0 ms use four SMs or all of them is exactly the question Figure 1 showed the number cannot answer.

## Implementation: timing a step without lying

The lab's harness wraps the loop in two clocks at once. The core is a dozen lines:

```python
import time
import torch

class TwoClocks:
    """Time each phase on the host clock and on the GPU's clock."""
    def __init__(self):
        self.marks = []                                  # (name, host_seconds, event)

    def mark(self, name):
        ev = torch.cuda.Event(enable_timing=True)
        ev.record()                                      # enqueued; returns at once
        self.marks.append((name, time.perf_counter(), ev))

    def report(self):
        torch.cuda.synchronize()                         # the only sync, after the step
        for (a, ta, ea), (_, tb, eb) in zip(self.marks, self.marks[1:]):
            print(f"{a:>12}  host {1e3 * (tb - ta):7.2f} ms   gpu {ea.elapsed_time(eb):7.2f} ms")
```

Call `mark("forward")` before the forward pass, `mark("backward")` before backward, and so on, with a final `mark("end")`. Phases whose GPU time is several times their host time are GPU-bound; phases where the two clocks agree are host-bound; a phase with a large host time and no GPU time is waiting on something, usually a sync point.

Removing the logging sync is a change of habit rather than of code. Keep the running loss on the device and read it rarely:

```python
running = torch.zeros((), device="cuda")
for step, (x, y) in enumerate(loader):
    ...
    running += loss.detach()            # stays on the GPU: no sync
    if step % 100 == 99:
        print(running.item() / 100)     # one sync per 100 steps
        running.zero_()
```

The optimizer needs only its default: leave `foreach` unset, or ask for `fused=True` where the optimizer offers it.  Capturing the whole step as a graph follows PyTorch's *whole-network capture* recipe — warm up on a side stream, capture into a `torch.cuda.CUDAGraph` with static input tensors, then copy each batch into those tensors and call `replay()` — and the lab includes it as a variant.  It only captures cleanly once the mid-step `.item()` is gone.  Everything here was checked against PyTorch 2.14.0 and the CUDA 13.4 Update 1 documentation. 

The lab's second script tests Figure 1 directly. It holds the GPU in `torch.cuda._sleep` — one thread in one block — while reading NVML's utilization, then does the same with a full-width kernel and with a stream of tiny launches, and records all three.

## Limitations and common mistakes

> [!WARNING]
> **Common mistake: `torch.cuda.synchronize()` after every line.** It makes each line's host time equal its GPU time, so the per-line numbers look right — and the step being measured is no longer the step that runs, because every sync destroys the overlap you were trying to see. NVIDIA's V100 measurement puts a price on it: 9.6 µs per kernel with a sync after each launch, against 3.8 µs without.  Use events and synchronize once, at the end.

**Timing a loop without a final synchronize.** After both fixes, the host issues a step in 2.6 ms while the GPU needs 15.0 ms. Time 20 steps with `perf_counter()` and no sync, and the model reports 2.6 ms per step — nearly six times too fast; the graphed version reports 0.02. In reality the queue is finite, so after enough launches the launch call itself starts to block and the number drifts toward the truth. NVIDIA documents that the queue can be scaled with `CUDA_SCALE_LAUNCH_QUEUES` but not how deep it is,  so how wrong the naive number is depends on how many steps you happened to time.

**The model is a model.** It has one stream, no launch latency, an unbounded queue and uniform costs. Real steps have data-loading and communication streams, and real launches cost different amounts. Its job is to make the mechanism checkable by hand; the Tier B script is the check against hardware.

**The utilization number has conditions of its own.** It is not supported on GPUs partitioned with MIG (Multi-Instance GPU), and with ECC (error-correcting memory) enabled it can read high during driver initialisation while memory is scrubbed.  Its sampling is contested, as above. One workshop paper defends it, granting that it does not measure SMs but calling it a good enough estimate for scheduling.  Dashboards built on DCGM should also know that version 4.6.0 renamed the profiling fields — SM Activity is now `DCGM_FI_PROF_SM_UTIL_RATIO`, field 1002, with the old `DCGM_FI_PROF_SM_ACTIVE` kept as a deprecated alias  — and that those metrics are sampled at 1 Hz by default and no faster than every 100 ms. 

**SM Activity is not efficiency either.** A warp stalled waiting on memory counts as active,  which is why DCGM calls 0.8 necessary but not sufficient.  NVIDIA's timeline profiler, Nsight Systems, carries rows for the same idea — *SMs Active*, and an *Idle SM Unused Warp Slots* row whose documented causes include "CPU starving the GPU"   — alongside separate host and GPU rows for every CUDA call and every stream.  Reading those rows is part 5's subject; what the SMs are doing inside a resident kernel is part 8's.

**Data loading is host-side time too.** This post held the batch constant. In real training the data pipeline can dominate: one study measured CPU pre-processing stalls of up to 65% of epoch time.  Part 5 begins exactly there.

## Key takeaways

- **`nvidia-smi` utilization is a clock, not a gauge.** It is the share of a 1/6–1 s window in which some kernel was executing,   with no term for how many SMs that kernel used; a single spinning thread reads 100%.
- **Two clocks find the missing time; one cannot.** A host timer measures issuing, CUDA events measure the stream. Where they disagree the GPU is the bottleneck; where they agree the host is; where the events read zero, the line only waited.
- **A sync point costs nothing and destroys overlap.** It turns one `max(host, GPU)` into a sum of maxes — 22.4 ms of work took 32.0 ms because of one `loss.item()`.
- **A launch costs microseconds and hides only behind a longer kernel.** Short kernels make the host the critical path; fewer, larger launches is the first fix.  
- **CUDA Graphs shorten the host lane, never the GPU lane.** They require static shapes and forbid sync points, so remove the syncs first. 

## Try it yourself

<details><summary>Move <code>losses.append(loss.item())</code> to after <code>opt.step()</code>. What does the host timer charge to it now, and how long is the step?</summary>

About 0.0 ms, and 22.4 ms. The optimizer's 1,000 launches now start at 2.4 ms and overlap forward and backward's execution. The GPU drains the queued optimizer kernels by about 13.7 ms and then keeps pace with the host, finishing the last kernel a few microseconds after the host issues it at 22.4 ms. By the time `loss.item()` runs, there is nothing left to wait for. The sync is still there; it just no longer sits between two things that could overlap — the same result as deleting it.

</details>

<details><summary>Keep the step as written, but make each optimizer kernel take 25 µs instead of 3 µs. What happens to the step time and to utilization?</summary>

The step gets *slower* — 37.0 ms instead of 32.0 — and utilization rises from 47% to essentially 100%. With 25 µs kernels and 20 µs launches, the optimizer is now GPU-bound: kernels queue up and the GPU never waits. In equation (3), segment B becomes $\max(20.0,\ 25.0) = 25.0$, so the step is 12.0 + 25.0 = 37.0 ms, all of it inside kernels. The job got worse and the dashboard got better. That is the title of this post.

</details>

<details><summary>A run with <code>torch.cuda.set_sync_debug_mode("error")</code> finishes without raising. Is the loop free of sync points?</summary>

No. PyTorch labels the mode experimental and states that not every synchronizing operation triggers it.  A clean run means none were detected. Pair it with the two-clock timer: a phase whose CUDA-event time is zero while its host time is large is waiting on something, whether or not the debug mode noticed.

</details>

## References

### Lab downloads

- [`README.md`](LAB_01) — the two hardware tiers, prerequisites, run order, expected results, the provenance line to record, and cleanup.
- [`queue_model.py`](LAB_02) — Tier A, no GPU: the one-stream model that prints every number in the worked example, the fixes and the exercises.
- [`step_timing.py`](LAB_03) — Tier B, one GPU: times a real training step on both clocks, lists its sync points, and repeats it without the sync, with foreach, and as a CUDA graph.
- [`util_probe.py`](LAB_04) — Tier B, one GPU: reads NVML utilization while the GPU runs a one-thread spin kernel, a full-width kernel, and a stream of tiny launches.
- [`expected-output.txt`](LAB_05) — the Tier A transcript as captured, and the Tier B sections marked not measured.
- [`results-schema.json`](LAB_06) — the empty schema both Tier B scripts fill, including the provenance fields.
- [Lab Download](https://minio.canery.in/media/lab-gpu-idle-at-100-percent-utilization.zip)

### Sources

**NVIDIA documentation**

- System Management Interface (`nvidia-smi`), *Utilization* field descriptions. [https://docs.nvidia.com/deploy/nvidia-smi/index.html](https://docs.nvidia.com/deploy/nvidia-smi/index.html) (accessed 2026-09-24)
- NVML API Reference, `nvmlUtilization_t`. [https://docs.nvidia.com/deploy/nvml-api/latest/api/structnvmlUtilization__t.html](https://docs.nvidia.com/deploy/nvml-api/latest/api/structnvmlUtilization__t.html) (accessed 2026-09-24)
- DCGM User Guide, *Feature Overview — Profiling Metrics*; DCGM Changelog 4.6.0. [https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html) (accessed 2026-09-24)
- Nsight Systems User Guide v2026.5, *GPU Metrics* and *CUDA Trace*. [https://docs.nvidia.com/nsight-systems/UserGuide/index.html](https://docs.nvidia.com/nsight-systems/UserGuide/index.html) (accessed 2026-09-24)
- CUDA Programming Guide v13.4.2, §2.5 *Asynchronous Execution* and §3.1.3 *More on Streams and Events*. [https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/asynchronous-execution.html](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/asynchronous-execution.html) (accessed 2026-09-24)
- CUDA Programming Guide v13.4.2, §4.2 *CUDA Graphs*. [https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/cuda-graphs.html](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/cuda-graphs.html) (accessed 2026-09-24)
- CUDA Programming Guide v13.4.2, §5.2 *CUDA Environment Variables*. [https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/environment-variables.html](https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/environment-variables.html) (accessed 2026-09-24)
- CUDA Runtime API 13.4, *Event Management*, *Stream Management*, *API synchronization behavior*. [https://docs.nvidia.com/cuda/cuda-runtime-api/api-sync-behavior.html](https://docs.nvidia.com/cuda/cuda-runtime-api/api-sync-behavior.html) (accessed 2026-09-24)
- CUDA Toolkit release notes, 12.0 through 13.4 Update 1. [https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html) (accessed 2026-09-24)
- A. Gray, "Getting Started with CUDA Graphs", NVIDIA Technical Blog, 2019. [https://developer.nvidia.com/blog/cuda-graphs/](https://developer.nvidia.com/blog/cuda-graphs/) (accessed 2026-09-24)
- H. Hoffman and F. Oh, "Constant Time Launch for Straight-Line CUDA Graphs and Other Performance Enhancements", NVIDIA Technical Blog, 2024. [https://developer.nvidia.com/blog/constant-time-launch-for-straight-line-cuda-graphs-and-other-performance-enhancements/](https://developer.nvidia.com/blog/constant-time-launch-for-straight-line-cuda-graphs-and-other-performance-enhancements/) (accessed 2026-09-24)

**PyTorch documentation and source (2.14)**

- *CUDA semantics* — asynchronous execution, CUDA streams, CUDA Graphs. [https://docs.pytorch.org/docs/2.14/notes/cuda.html](https://docs.pytorch.org/docs/2.14/notes/cuda.html) (accessed 2026-09-24)
- `torch.cuda.set_sync_debug_mode` and `torch.cuda.Event`. [https://docs.pytorch.org/docs/2.14/generated/torch.cuda.set_sync_debug_mode.html](https://docs.pytorch.org/docs/2.14/generated/torch.cuda.set_sync_debug_mode.html) (accessed 2026-09-24)
- *Performance Tuning Guide*. [https://docs.pytorch.org/tutorials/recipes/recipes/tuning_guide.html](https://docs.pytorch.org/tutorials/recipes/recipes/tuning_guide.html) (accessed 2026-09-24)
- *A guide on good usage of `non_blocking` and `pin_memory()`*. [https://docs.pytorch.org/tutorials/intermediate/pinmem_nonblock.html](https://docs.pytorch.org/tutorials/intermediate/pinmem_nonblock.html) (accessed 2026-09-24)
- `torch.optim` — *Algorithms*. [https://docs.pytorch.org/docs/2.14/optim.html](https://docs.pytorch.org/docs/2.14/optim.html) (accessed 2026-09-24)
- *CUDAGraph Trees* and `torch.compile`. [https://docs.pytorch.org/docs/2.14/user_guide/torch_compiler/torch.compiler_cudagraph_trees.html](https://docs.pytorch.org/docs/2.14/user_guide/torch_compiler/torch.compiler_cudagraph_trees.html) (accessed 2026-09-24)
- `aten/src/ATen/cuda/Sleep.cu` and `c10/cuda/CUDAStream.cpp` at tag v2.14.0. [https://github.com/pytorch/pytorch/blob/v2.14.0/aten/src/ATen/cuda/Sleep.cu](https://github.com/pytorch/pytorch/blob/v2.14.0/aten/src/ATen/cuda/Sleep.cu)
- V. Nguyen et al., "Accelerating PyTorch with CUDA Graphs", PyTorch Blog, 2021. [https://pytorch.org/blog/accelerating-pytorch-with-cuda-graphs/](https://pytorch.org/blog/accelerating-pytorch-with-cuda-graphs/) (accessed 2026-09-24)

**Literature**

- Y. Gao et al., "An Empirical Study on Low GPU Utilization of Deep Learning Jobs", IEEE/ACM ICSE 2024. [https://doi.org/10.1145/3597503.3639232](https://doi.org/10.1145/3597503.3639232)
- M. Jeon et al., "Analysis of Large-Scale Multi-Tenant GPU Clusters for DNN Training Workloads", USENIX ATC 2019. [https://www.usenix.org/conference/atc19/presentation/jeon](https://www.usenix.org/conference/atc19/presentation/jeon)
- J. Gleeson et al., "RL-Scope: Cross-Stack Profiling for Deep Reinforcement Learning Workloads", MLSys 2021. [https://arxiv.org/abs/2102.04285](https://arxiv.org/abs/2102.04285)
- G. Yeung et al., "Towards GPU Utilization Prediction for Cloud Deep Learning", USENIX HotCloud 2020. [https://www.usenix.org/conference/hotcloud20/presentation/yeung](https://www.usenix.org/conference/hotcloud20/presentation/yeung)
- A. Paszke et al., "PyTorch: An Imperative Style, High-Performance Deep Learning Library", NeurIPS 2019. [https://arxiv.org/abs/1912.01703](https://arxiv.org/abs/1912.01703)
- W. Kwon, G.-I. Yu, E. Jeong, B.-G. Chun, "Nimble: Lightweight and Parallel GPU Task Scheduling for Deep Learning", NeurIPS 2020. [https://arxiv.org/abs/2012.02732](https://arxiv.org/abs/2012.02732)
- J. Ansel et al., "PyTorch 2: Faster Machine Learning Through Dynamic Python Bytecode Transformation and Graph Compilation", ASPLOS 2024. [https://doi.org/10.1145/3620665.3640366](https://doi.org/10.1145/3620665.3640366)
- B. Zheng et al., "Grape: Practical and Efficient Graph-based Executions for Dynamic Deep Neural Networks on GPUs", MICRO 2023. [https://doi.org/10.1145/3613424.3614248](https://doi.org/10.1145/3613424.3614248)
- A. Ghosh, A. Nayak, A. Panwar, A. Basu, "GraCE: Unlocking CUDA Graphs with Compiler Support for ML Workloads", USENIX OSDI 2026. [https://www.usenix.org/system/files/osdi26-ghosh.pdf](https://www.usenix.org/system/files/osdi26-ghosh.pdf)
- J. Mohan, A. Phanishayee, A. Raniwala, V. Chidambaram, "Analyzing and Mitigating Data Stalls in DNN Training", PVLDB 14(5), 2021. [https://doi.org/10.14778/3446095.3446100](https://doi.org/10.14778/3446095.3446100)
