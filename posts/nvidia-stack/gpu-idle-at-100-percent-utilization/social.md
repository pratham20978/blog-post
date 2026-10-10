---
social_schema: 2
canonical_url: "https://canery.in/blogs/gpu-idle-at-100-percent-utilization"
---

# Social publishing package — gpu-idle-at-100-percent-utilization

## LinkedIn post

`nvidia-smi` says your GPU is at 100%. The training step is still twice as slow as the arithmetic says it should be. Both are true, and the first tells you almost nothing about the second.

NVIDIA defines that number as the share of a 1/6–1 second window in which *some* kernel was executing. It has no term for how much of the chip the kernel used. A single thread spinning in one block reads 100%.

So where does the time go in a slow step? Usually to the host, and a Python timer will send you to the wrong line:

→ Kernel launches are asynchronous. `model(x)` returns after queuing the work, not after doing it.
→ `loss.item()` in the middle of a step has to wait for everything queued ahead of it — and the timer bills that wait to the logging line.
→ Time the same step with CUDA events and the bill moves back: in the article's worked example, 9.6 ms "of logging" turns out to be forward and backward still running on the GPU.

The rule I keep coming back to: a sync point costs almost nothing itself. It costs the overlap it destroys. Remove one `loss.item()` and the example step goes from 32.0 ms to 22.4 ms without touching a kernel. Cut the optimizer's 1,000 launches to 10 and it reaches 15.0 ms — at which point the dashboard reads 100%, and stops being able to tell you anything.

Also in the article: what a kernel launch actually costs (NVIDIA measured 9.6 µs per kernel for a 2.9 µs kernel when every launch waits for the last), and what CUDA Graphs remove and cannot remove.

The worked example is a model you can run with no GPU; the GPU harness ships with an empty results file because nothing in it is invented.

## LinkedIn first comment

A graph shortens the host lane. It cannot shorten the GPU lane — and it forbids the sync points you would need to remove first anyway.

Read the full article on Canery: https://canery.in/blogs/gpu-idle-at-100-percent-utilization

## Instagram caption

Your GPU reads 100% and the job is still slow. That number is a clock, not a gauge: it counts the time some kernel was running, not how much of the chip was working.

Swipe for what 100% actually measures, one training step timed on two clocks, the one logging line that costs 30% of the step, what a kernel launch costs, and what CUDA Graphs cannot fix.

Every number is sourced or computed by a script you can run on a laptop with no GPU.

Link in bio.

#cuda #nvidia #gpu #pytorch #machinelearning #mlops #performance #deeplearning

## Shared feed order

1. `assets/social/feed-01-a-clock-not-a-gauge.png` — what `nvidia-smi`'s 100% measures, against SM Activity
2. `assets/social/feed-02-two-clocks.png` — one training step, host timer against CUDA events
3. `assets/social/feed-03-a-sync-point-costs-overlap.png` — the max-per-segment arithmetic of a sync point
4. `assets/social/feed-04-what-a-launch-costs.png` — NVIDIA's V100 launch-cost measurement
5. `assets/social/feed-05-what-graphs-cannot-remove.png` — what a CUDA graph removes, keeps and adds
6. `assets/social/feed-06-read-the-article.png` — the step fixed twice, 32.0 to 15.0 ms, and the CTA

## Instagram Story

- CTA: Your GPU says 100% and the job is still slow. Here is where the time actually goes — tap the link.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/gpu-idle-at-100-percent-utilization

### Story order

1. `assets/social/story-01-one-thread.png` — Overlay: One thread, one busy SM, and the dashboard says 100%.
2. `assets/social/story-02-the-line-that-waited.png` — Overlay: The timer blamed logging. The GPU says logging did nothing.
3. `assets/social/story-03-the-order-of-fixes.png` — Overlay: Syncs first, launches second, graphs last.
4. `assets/social/story-04-read-the-article.png` — Overlay: Time your step on two clocks. Link above.

## Asset metadata

### feed-01-a-clock-not-a-gauge

- File: `assets/social/feed-01-a-clock-not-a-gauge.png`
- Title: 100% is a clock, not a gauge
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: nvidia-smi's utilization counts time with some kernel running; it cannot tell one busy SM from a full chip.
- Technical source: Article section "The problem: a clock, not a gauge" and Figure 1; ledger claims L01, L05, L06.
- Visual structure: Serif headline and two-line deck, then three side-by-side panels each holding an SM-by-time grid, an nvidia-smi reading and a DCGM SM Activity reading; the first two panels are accent-bordered; takeaway above the footer.
- Visible-text transcript: 100% is a clock, not a gauge. / nvidia-smi counts the time some kernel was running. It never asks how much of the GPU that kernel used. / ONE BLOCK — nvidia-smi 100% — SM Activity 1/N — disagree / N/5 BLOCKS — nvidia-smi 100% — SM Activity 0.20 — disagree / N BLOCKS — nvidia-smi 100% — SM Activity 1.00 — agree / One spinning thread reads 100%. So does a full chip. The number cannot tell them apart. / WHY YOUR GPU IS IDLE AT 100% · CANERY.IN
- Alt text: Three panels of SM grids: one block, a fifth of the chip and the full chip all read 100% utilization, with SM Activity 1/N, 0.20 and 1.00.
- Long description: A branded 1080×1350 card. Three panels each draw a grid of streaming multiprocessors against time within one sample window. In the first, one row is filled: a single block. In the second, two rows of ten: N/5 blocks. In the third, every cell: N blocks. All three read 100% on nvidia-smi, whose documented definition is the share of the window during which any kernel was executing. Their DCGM SM Activity readings are 1/N, 0.20 and 1.00 — DCGM's own worked example. The first two panels are marked as readings that disagree; the takeaway notes that a single spinning thread and a full chip read the same.
- Keywords: nvidia-smi, GPU utilization, DCGM, SM Activity, streaming multiprocessor, CUDA
- Canonical URL: https://canery.in/blogs/gpu-idle-at-100-percent-utilization

### feed-02-two-clocks

- File: `assets/social/feed-02-two-clocks.png`
- Title: One step, two clocks
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: A host timer and CUDA events agree on the step's total and disagree on where it went.
- Technical source: Article section "Worked example: one training step, timed twice" and Figure 3; values from lab/queue_model.py (model inputs, not a measurement).
- Visual structure: Headline and deck, a small caption, then a bordered table with host-timer and CUDA-event columns for four phases and the whole step; the loss.item() row is highlighted; a single accent line beneath.
- Visible-text transcript: One step, two clocks. / A host timer measures when each Python line returned. CUDA events measure when the GPU got there. / THE SAME STEP, TWO CLOCKS · MODEL INPUTS, NOT A MEASUREMENT / HOST TIMER / CUDA EVENTS / forward 0.8 ms 4.0 ms / backward 1.6 ms 8.0 ms / loss.item() 9.6 ms 0.0 ms / optimizer 20.0 ms 20.0 ms / whole step 32.0 ms 32.0 ms / same total, a different bill / The timer billed 9.6 ms to the one line that did no work at all. / WHY YOUR GPU IS IDLE AT 100% · CANERY.IN
- Alt text: A table timing one training step twice: the host timer bills 9.6 ms to loss.item(); CUDA events show 0.0 ms there and 4.0 and 8.0 ms in forward and backward.
- Long description: A branded 1080×1350 card from the article's worked example, labelled as model inputs rather than a measurement. Four phases are timed on the host clock and on CUDA events. Forward reads 0.8 ms on the host and 4.0 ms on events; backward 1.6 and 8.0; loss.item() 9.6 and 0.0; the optimizer 20.0 on both. Both clocks total 32.0 ms. The highlighted loss.item() row is the point: the host timer charges the logging line for time the GPU spent finishing forward and backward.
- Keywords: CUDA events, torch.cuda.Event, time.perf_counter, loss.item, synchronization, PyTorch
- Canonical URL: https://canery.in/blogs/gpu-idle-at-100-percent-utilization

### feed-03-a-sync-point-costs-overlap

- File: `assets/social/feed-03-a-sync-point-costs-overlap.png`
- Title: A sync point costs the overlap
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: A sync point turns one max(host, GPU) into a sum of per-segment maxes.
- Technical source: Article section "The math: a sync point turns one max into a sum", equation (3); values from lab/queue_model.py.
- Visual structure: Headline and deck, a caption naming what each max compares, then two large formula panels — with the sync (accent) and without it — and an accent line stating the inequality.
- Visible-text transcript: A sync point costs the overlap. / loss.item() does no work. It stops the host issuing while the GPU is still running. / EACH MAX( ) IS HOST ISSUE TIME VS GPU TIME · MODEL INPUTS / ONE MAX PER SEGMENT — with loss.item() mid-step — max(2.4, 12.0) + max(20.0, 3.0) = 12.0 + 20.0 = 32.0 ms / ONE MAX FOR THE WHOLE STEP — without it — max(2.4 + 20.0, 12.0 + 3.0) = max(22.4, 15.0) = 22.4 ms / the sum of the maxes never beats the max of the sums / One logging line: 9.6 ms of a 32.0 ms step, gone the moment the value stays on the GPU. / WHY YOUR GPU IS IDLE AT 100% · CANERY.IN
- Alt text: Two formulas: with loss.item() mid-step the step is 12.0 + 20.0 = 32.0 ms; without it, max(22.4, 15.0) = 22.4 ms.
- Long description: A branded 1080×1350 card. Each max compares a segment's host issuing time with its GPU time. With loss.item() between backward and the optimizer, the step is two separately maxed segments: max(2.4, 12.0) for forward and backward plus max(20.0, 3.0) for the optimizer, 32.0 ms. Without the sync, one max covers the whole step: max(22.4, 15.0), 22.4 ms. Because a sum of maxes is never smaller than the max of the sums, the difference — 9.6 ms here — is the cost of the sync point itself.
- Keywords: synchronization point, overlap, asynchronous execution, CUDA stream, loss.item, performance model
- Canonical URL: https://canery.in/blogs/gpu-idle-at-100-percent-utilization

### feed-04-what-a-launch-costs

- File: `assets/social/feed-04-what-a-launch-costs.png`
- Title: A launch costs microseconds
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The same 2.9 µs kernel costs 9.6 µs per launch when each launch waits for the last, 3.8 µs when launches overlap, 3.4 µs as a graph.
- Technical source: Article section "What does a kernel launch cost?" and Figure 8; ledger claim L55 (Gray, NVIDIA Technical Blog, 2019).
- Visual structure: Headline and deck, a caption, then three horizontal bars each split into a dark kernel segment and an orange overhead segment with the total at the end; a key and the setup line beneath.
- Visible-text transcript: A launch costs microseconds. / Cheap in absolute terms. Expensive next to a kernel that only runs for a few of them. / ONE SHORT KERNEL, 20,000 LAUNCHES, NVIDIA'S V100 TEST / sync after every launch 9.6 µs / launches overlap execution 3.8 µs / one cuda graph per step 3.4 µs / dark: the 2.9 µs kernel · orange: overhead / Tesla V100, CUDA 10.1, measured by NVIDIA / A launch hides only behind a kernel that runs longer than the launch takes. / WHY YOUR GPU IS IDLE AT 100% · CANERY.IN
- Alt text: Bars of per-kernel cost on a V100: 9.6 µs with a sync after each launch, 3.8 µs overlapped, 3.4 µs as a CUDA graph, for a 2.9 µs kernel.
- Long description: A branded 1080×1350 card charting NVIDIA's own measurement on a Tesla V100 with CUDA 10.1: an element-wise kernel of 2.9 µs launched 20 times per step for 1,000 steps. With a synchronize after every launch, each kernel effectively costs 9.6 µs; when launches overlap the previous kernel's execution, 3.8 µs; captured as one CUDA graph per step, 3.4 µs. Each bar shows the 2.9 µs of kernel in dark and the overhead in orange, so the hidden and exposed launch cost is visible directly.
- Keywords: kernel launch overhead, CUDA Graphs, cudaStreamSynchronize, V100, NVIDIA, microseconds
- Canonical URL: https://canery.in/blogs/gpu-idle-at-100-percent-utilization

### feed-05-what-graphs-cannot-remove

- File: `assets/social/feed-05-what-graphs-cannot-remove.png`
- Title: What a CUDA graph cannot remove
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: A graph replaces many launches with one; kernel time, CPU work outside it and sync points survive, and it adds capture cost and static shapes.
- Technical source: Article section "What do CUDA Graphs remove, and what do they not?" and Figure 9; ledger claims L65, L67, L56, L69.
- Visual structure: Headline and deck, then three stacked cards — removed (accent), survives, added — each with a short list.
- Visible-text transcript: What a CUDA graph cannot remove. / A graph replays a captured step with one launch. It does nothing about the work inside it. / ONE LAUNCH REPLACES MANY — removed — per-kernel host launch cost: Python, C++ and driver dispatch / WHAT A GRAPH CANNOT TOUCH — survives — every kernel's execution time; CPU work outside the graph; sync points, which capture forbids / WHAT IT COSTS — added — capture and instantiation, once; static shapes, a private memory pool / A graph shortens the host lane. It cannot shorten the GPU lane. / WHY YOUR GPU IS IDLE AT 100% · CANERY.IN
- Alt text: Three cards on CUDA graphs: launch overhead removed; kernel time, outside CPU work and sync points survive; capture cost and static shapes added.
- Long description: A branded 1080×1350 card. The first card lists what a graph replay removes: the per-kernel host cost of launching, across Python, C++ and the CUDA driver. The second lists what survives: every kernel's execution time, CPU work outside the captured region, and sync points, which stream capture forbids and which therefore have to be removed before capture. The third lists what a graph adds: a one-time capture and instantiation cost, static shapes, and a graph-private memory pool.
- Keywords: CUDA Graphs, stream capture, torch.cuda.graph, reduce-overhead, launch overhead, PyTorch
- Canonical URL: https://canery.in/blogs/gpu-idle-at-100-percent-utilization

### feed-06-read-the-article

- File: `assets/social/feed-06-read-the-article.png`
- Title: The same step, fixed twice
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: Removing the mid-step sync and then the optimizer's launches takes the step from 32.0 to 15.0 ms, and utilization from 47% to 100%.
- Technical source: Article section "The math" and Figure 10; values from lab/queue_model.py (model inputs).
- Visual structure: Headline of three numbers and a deck, a caption, then three stacked rows — as written, fix 1, fix 2 — each with a step time and a utilization; the last highlighted; the CTA footer.
- Visible-text transcript: 32.0, 22.4, 15.0 ms. / Drop the mid-step sync, then cut the optimizer's launches. Nothing about the kernels changed. / THE WORKED EXAMPLE, FIXED TWICE · MODEL INPUTS / as written — loss.item() mid-step — 32.0 ms — util 47% / fix 1 — log outside the step — 22.4 ms — util 67% / fix 2 — optimizer as 10 launches — 15.0 ms — util 100% / utilization by nvidia-smi's definition / The last one reads 100%: the point where the number stops telling you anything. / READ IT AT CANERY.IN/BLOGS/GPU-IDLE-AT-100-PERCENT-UTILIZATION
- Alt text: Three versions of one step: 32.0 ms at 47% utilization, 22.4 ms at 67%, and 15.0 ms at 100%, with the article link.
- Long description: A branded 1080×1350 closing card from the article's model. As written, with loss.item() in the middle of the step and a 1,000-launch optimizer, the step takes 32.0 ms and reads 47% by nvidia-smi's definition. Moving the logging out of the step gives 22.4 ms and 67%. Issuing the optimizer as 10 launches gives 15.0 ms and 100%. No kernel changed between the three. The takeaway makes the article's point that 100% is exactly where the utilization number stops being informative.
- Keywords: GPU utilization, training step, synchronization, kernel launches, CUDA, PyTorch performance
- Canonical URL: https://canery.in/blogs/gpu-idle-at-100-percent-utilization

### story-01-one-thread

- File: `assets/social/story-01-one-thread.png`
- Title: 100% busy, one thread
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: A single thread in one block holds utilization at 100% while every other SM is idle.
- Technical source: Article section "The problem: a clock, not a gauge"; ledger claims L01, L50.
- Visual structure: Lockup and counter, two-line serif headline over a deck, then a readout panel with 100% in the accent, a large grid of SMs with only the first lit, and a caption.
- Visible-text transcript: 100% busy. One thread. / The utilization number counts time, not how much of the chip is working. / utilization.gpu 100% / one kernel resident · one SM busy / By NVIDIA's own definition, this reads 100%. / WHY YOUR GPU IS IDLE AT 100% · CANERY.IN
- Alt text: A utilization readout of 100% above a grid of grey SMs in which only one is lit.
- Long description: A branded 1080×1920 Story cover. A readout labelled utilization.gpu shows 100% in the accent colour. Beneath it, a grid of 128 grey squares stands for the GPU's streaming multiprocessors, with only the first lit. The caption reads one kernel resident, one SM busy. The takeaway states that NVIDIA's own definition — the share of time some kernel was executing — makes this read 100%.
- Keywords: nvidia-smi, GPU utilization, streaming multiprocessor, torch.cuda._sleep, CUDA
- Canonical URL: https://canery.in/blogs/gpu-idle-at-100-percent-utilization

### story-02-the-line-that-waited

- File: `assets/social/story-02-the-line-that-waited.png`
- Title: The line that only waited
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: loss.item() reads 9.6 ms on the host timer and 0.0 ms on CUDA events: it did no work and only waited.
- Technical source: Article section "Worked example: one training step, timed twice" and Figure 3; values from lab/queue_model.py.
- Visual structure: Lockup and counter, headline and deck, a caption, two stacked cards contrasting the host timer (accent) with the CUDA events, and an accent line giving the arithmetic of the wait.
- Visible-text transcript: The line that only waited. / A sync point in the middle of a training step, timed on two clocks. / LOSS.ITEM() IN THE MIDDLE OF A STEP · MODEL INPUTS / WHAT THE TIMER SAID — host timer: 9.6 ms — the Python line took this long to return / WHAT THE GPU DID — CUDA events: 0.0 ms — no kernel ran in that time; the host was waiting in line / 12.0 ms of queued GPU work, less the 2.4 spent issuing it / It did no work. It made the host stop issuing while the GPU ran. / WHY YOUR GPU IS IDLE AT 100% · CANERY.IN
- Alt text: loss.item() reads 9.6 ms on a host timer and 0.0 ms on CUDA events; the wait was queued GPU work.
- Long description: A branded 1080×1920 Story frame from the article's model. The host timer says loss.item() took 9.6 ms to return. CUDA events recorded around the same line show 0.0 ms: no kernel ran during it. The 9.6 ms is the 12.0 ms of forward and backward work the GPU still had queued, less the 2.4 ms the host had already spent issuing it — time the logging line was billed for but never used.
- Keywords: loss.item, synchronization point, CUDA events, host timer, PyTorch
- Canonical URL: https://canery.in/blogs/gpu-idle-at-100-percent-utilization

### story-03-the-order-of-fixes

- File: `assets/social/story-03-the-order-of-fixes.png`
- Title: Syncs, launches, then graphs
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: The fixes go in a fixed order — remove sync points, reduce launches, graph what remains — because graphs forbid sync points.
- Technical source: Article sections "What do CUDA Graphs remove, and what do they not?" and "The math"; ledger claim L67; values from lab/queue_model.py.
- Visual structure: Lockup and counter, headline and deck, a caption, then three numbered rows, the second highlighted.
- Visible-text transcript: Syncs, launches, then graphs. / The order matters: CUDA graphs forbid sync points, so the first fix is not optional. / THE ORDER THE FIXES GO IN / 1 remove the mid-step sync 32.0 → 22.4 ms / 2 fewer, larger launches 22.4 → 15.0 ms / 3 graph what is left one launch per step / Fix the host lane before reaching for a graph. / WHY YOUR GPU IS IDLE AT 100% · CANERY.IN
- Alt text: Three numbered fixes: remove the sync (32.0 to 22.4 ms), fewer launches (22.4 to 15.0 ms), then graph what is left.
- Long description: A branded 1080×1920 Story frame. Three numbered rows give the order of fixes from the article's worked example. First, remove the mid-step sync point: 32.0 to 22.4 ms. Second, issue fewer, larger launches, as a foreach or fused optimizer does: 22.4 to 15.0 ms. Third, capture what is left as a CUDA graph, one launch per step. The deck explains why the order is forced: stream capture prohibits synchronizing calls such as loss.item().
- Keywords: CUDA Graphs, foreach optimizer, synchronization, kernel launches, PyTorch performance
- Canonical URL: https://canery.in/blogs/gpu-idle-at-100-percent-utilization

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: Time it on two clocks
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: A host timer and CUDA events side by side, read together, name each phase GPU-bound, host-bound or a sync point.
- Technical source: Article section "Implementation: timing a step without lying"; ledger claims L27, L39, L40.
- Visual structure: Lockup and counter, headline and deck, a caption, a code panel, then an accent panel pairing each reading with its diagnosis, and the CTA line.
- Visible-text transcript: Time it on two clocks. / A host timer and CUDA events, side by side, and one synchronize at the very end. / A DOZEN LINES, IN THE ARTICLE / ev = torch.cuda.Event(enable_timing=True) / ev.record() # returns at once / t = time.perf_counter() / ... / torch.cuda.synchronize() # once, at the end / READ THE TWO TOGETHER / events far above host GPU-bound / the two agree host-bound / events near zero a sync point / The full article is on Canery. / LINK IN THE STICKER ABOVE
- Alt text: A code panel recording CUDA events beside a host timer, with a key: events above host is GPU-bound, equal is host-bound, near zero is a sync.
- Long description: A branded 1080×1920 closing Story frame. The code panel shows the core of the article's two-clock timer: create a CUDA event with timing enabled, record it — which returns at once — read time.perf_counter beside it, and synchronize once at the end of the step. The panel beneath gives the diagnosis the two readings support: events far above the host time mean the phase is GPU-bound, equal readings mean it is host-bound, and events near zero mean the line was a sync point. The frame closes with a pointer to the link sticker.
- Keywords: CUDA events, torch.cuda.Event, perf_counter, profiling, PyTorch, synchronization
- Canonical URL: https://canery.in/blogs/gpu-idle-at-100-percent-utilization
