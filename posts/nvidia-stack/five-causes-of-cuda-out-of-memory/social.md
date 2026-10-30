---
social_schema: 2
canonical_url: "https://canery.in/blogs/five-causes-of-cuda-out-of-memory"
---

# Social publishing package — five-causes-of-cuda-out-of-memory

## LinkedIn post

"CUDA out of memory. Tried to allocate 256.00 MiB." That first line is the same whatever filled the card, and most people stop reading there.

Part 4 of The NVIDIA Stack makes one 20 GiB model fail five different ways on an emulated 24 GiB card, with PyTorch 2.15.0, and reads the numbers after the first line:

→ 4.63 GiB free and a 256 MiB request refused: fragmentation, 37 free tails pinned beside live tensors
→ +1.55 GiB per batch: an evaluation loop without no_grad keeping every graph alive, whose last message looks like fragmentation
→ "Process 189145 has 6.17 GiB": a live orphan, not a zombie; an unreaped zombie gave its memory back
→ 4.33 GiB in the process but outside PyTorch's books: a library's own pool
→ 23.25 GiB allocated and nothing else holding memory: capacity

And calling torch.cuda.empty_cache() before a retry failed in both runs where it was tried: before raising, the allocator had already released every cached segment that was free at the failure.

The cards walk through the evidence and the order to read it in.

## LinkedIn first comment

Read growth first, then reserved-but-unallocated against the request, then the other holders; what is left is capacity.

Read the full article on Canery: https://canery.in/blogs/five-causes-of-cuda-out-of-memory

## Instagram caption

One error message, five unrelated causes. PyTorch's CUDA out-of-memory error prints the same first line whether memory is fragmented, leaking one batch at a time, held by another process, held outside PyTorch, or simply too small, and the numbers after it say which. Measured on one GPU with PyTorch 2.15.0, with a lab that reproduces all five. Full article and lab: canery.in/blogs/five-causes-of-cuda-out-of-memory

#CUDA #PyTorch #GPU #MachineLearning #Debugging #DeepLearning

## Shared feed order

1. `assets/social/feed-01-one-message-five-causes.png` — The same first line of a CUDA out-of-memory error hides five unrelated causes
2. `assets/social/feed-02-fragmentation.png` — Doubling the batch left 37 free 128 MiB tails pinned beside live 256 MiB tensors
3. `assets/social/feed-03-retained-graph.png` — An evaluation loop without no_grad kept each batch's autograd graph and 33 saved tensors alive, growing 1.55 GiB a batch
4. `assets/social/feed-04-zombie-or-orphan.png` — An unreaped zombie gave its GPU memory back within a fraction of a second, while a live orphan kept 6.17 GiB and was named in the out-of-memory message
5. `assets/social/feed-05-outside-pytorch.png` — Memory a process holds outside PyTorch's allocator, measured on the GB10: a 173 MiB lazy context, 943 MiB eager, 548 MiB more for NCCL on one rank, and run 5's library pool at 4.33 GiB
6. `assets/social/feed-06-empty-cache.png` — Calling torch.cuda.empty_cache() and retrying failed in both runs it was tried in, because the allocator had already released every cached segment that was free at the failure
7. `assets/social/feed-07-read-in-this-order.png` — The decision tree as five ordered questions, each answered by one number from the lab's five runs, with growth checked first
8. `assets/social/feed-08-read-the-article.png` — The article's five causes with one measured number each, and where to read it

## Instagram Story

Not produced: this part ships feed cards only, at the owner's request (2026-10-30), so there are no Story frames, Story CTA or link sticker to post.

### Story order

None.

## Asset metadata

### feed-01-one-message-five-causes

- File: `assets/social/feed-01-one-message-five-causes.png`
- Title: Five causes, one OOM message
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: The same first line of a CUDA out-of-memory error hides five unrelated causes; run 1's message shows the numbers that tell them apart, with reserved-but-unallocated deciding this one
- Technical source: The problem: one message, six numbers; Figure 1; Worked example table
- Visual structure: lockup and counter; serif title; deck; a panel of four labelled numbers from run 1's message, the deciding 4.63 GiB in tangerine; a note naming the five causes; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · Five causes, · one OOM message. · PyTorch prints the same first line for five · unrelated problems. The numbers differ. · run 1's message: PyTorch 2.15.0, an emulated 24 GiB card · tried to allocate · 256 MiB · allocated by PyTorch · 19.00 GiB · reserved, unallocated · 4.63 GiB · the number that decides: fragmentation · other processes · none · the same first line comes from growth, fragmentation, · another process, memory outside PyTorch, or capacity · Don't stop at the first line: the cause · is in the numbers after it. · FIVE CAUSES OF ONE CUDA OOM · CANERY.IN
- Alt text: Card with run 1's out-of-memory numbers: a 256 MiB request, 19.00 GiB allocated, 4.63 GiB reserved but unallocated, no other process.
- Long description: Run 1 of the lab doubled the batch of a 20 GiB stand-in model on an emulated 24 GiB card, with PyTorch 2.15.0. Its message asked for 256 MiB, with 19.00 GiB allocated by PyTorch and 4.63 GiB reserved by PyTorch but unallocated, and listed no other process. The reserved-but-unallocated number decides the cause, fragmentation. The same first line comes from five causes: growth across iterations, fragmentation, another process, memory outside PyTorch, or capacity; the takeaway is to read the numbers after the first line.
- Keywords: CUDA out of memory, PyTorch, caching allocator, reserved memory, fragmentation, debugging
- Canonical URL: https://canery.in/blogs/five-causes-of-cuda-out-of-memory

### feed-02-fragmentation

- File: `assets/social/feed-02-fragmentation.png`
- Title: 4.63 GiB free, 256 MiB refused
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Doubling the batch left 37 free 128 MiB tails pinned beside live 256 MiB tensors; 4.63 GiB was free in 38 pieces and none held the 256 MiB request
- Technical source: Why does a 256 MiB request fail with 4.63 GiB free?; Figure 5; ledger L07, L09, L10
- Visual structure: lockup and counter; serif title; deck; a grid of 37 segments, each a dark live block and a tangerine free tail; the dashed 256 MiB request; the total free; a definition; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · 4.63 GiB free. · 256 MiB refused. · Doubling the batch left 128 MiB tails · pinned beside long-lived tensors. · batch doubled: 37 segments of 384 MiB, each a live · 256 MiB tensor and a free 128 MiB tail · the request: 256 MiB, larger than any tail · free in all: 4.63 GiB, in 38 pieces · fragmentation: free memory that cannot be used because · it sits beside live tensors, in pieces too small · Unallocated at least the request means · fragmentation: try expandable segments. · FIVE CAUSES OF ONE CUDA OOM · CANERY.IN
- Alt text: Grid of 37 segments, each a live 256 MiB tensor beside a free 128 MiB tail, next to a 256 MiB request that fits in none of them.
- Long description: In run 1 the batch was doubled, so every activation was 384 MiB. During the first backward pass and optimizer step, 256 MiB gradients and Adam states were placed in the freed 384 MiB blocks, leaving 37 free tails of 128 MiB pinned beside live tensors. At the failure PyTorch held 4.63 GiB reserved but unallocated in 38 pieces, yet the 256 MiB request fit in none of them. Reserved-but-unallocated memory at least as large as the request is the sign of fragmentation; PyTorch's expandable_segments setting is the first fix to try.
- Keywords: fragmentation, PyTorch caching allocator, expandable segments, reserved but unallocated, GPU memory
- Canonical URL: https://canery.in/blogs/five-causes-of-cuda-out-of-memory

### feed-03-retained-graph

- File: `assets/social/feed-03-retained-graph.png`
- Title: A leak can look like fragmentation
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: An evaluation loop without no_grad kept each batch's autograd graph and 33 saved tensors alive, growing 1.55 GiB a batch; its final message reads as fragmentation, so growth is checked first
- Technical source: What keeps memory growing from step to step?; Figure 7; Worked example run 3
- Visual structure: lockup and counter; serif title; deck; a small chart of allocated memory per evaluation batch, the leaking loop rising in tangerine to the allowance and the no_grad loop flat in blue; notes; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · A leak can look · like fragmentation. · An evaluation loop without no_grad kept · every batch's graph, and its tensors, alive. · allocated memory at the start of each evaluation batch · 10 · 15 · 20 · 25 · allowed 23.67 GiB · fails · +1.55 GiB · per batch · 33 saved · tensors · × 48 MiB · no_grad: · flat · GiB, batches 0 to 11 · at the failure 514 MiB was unallocated against a 48 MiB · request: on its own, that message reads as fragmentation · Check growth first: allocated memory at · the same point of two iterations. · FIVE CAUSES OF ONE CUDA OOM · CANERY.IN
- Alt text: Chart of allocated memory per evaluation batch: rising 1.55 GiB a batch to failure without no_grad, flat at 12 GiB with it.
- Long description: Run 3 evaluated batches of 1,536 rows, accumulating total = total + loss without torch.no_grad(). Each batch's autograd graph kept 33 saved tensors of 48 MiB alive, so allocated memory at the start of each batch rose 1.55 GiB, from 12.00 GiB until the eighth batch failed below the 23.67 GiB allowance. The same loop under no_grad, summing loss.item(), stayed flat. At the failure 514 MiB was unallocated against a 48 MiB request, which on its own reads as fragmentation; checking growth between iterations first avoids that misreading.
- Keywords: retained autograd graph, memory leak, torch.no_grad, evaluation loop, PyTorch, out of memory
- Canonical URL: https://canery.in/blogs/five-causes-of-cuda-out-of-memory

### feed-04-zombie-or-orphan

- File: `assets/social/feed-04-zombie-or-orphan.png`
- Title: The zombie isn't holding your GPU
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: An unreaped zombie gave its GPU memory back within a fraction of a second, while a live orphan kept 6.17 GiB and was named in the out-of-memory message
- Technical source: Who else is holding the card?; Worked example run 4; ledger L38, L39
- Visual structure: lockup and counter; serif title; deck; a three-row timeline of a child that exits without being reaped; a rule; the orphan's parent, state and the message line naming it; notes; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · The zombie isn't · holding your GPU. · A process that exited gives its memory back. · One that never exited keeps it. · a child that held 6 GiB exits; its parent never reaps it · 0.00 s · running, listed by NVML · 0.27 s · a zombie (state Z), still listed · 0.40 s · still a zombie, gone: MemFree +6.61 GiB · a leftover job whose parent was killed · parent PID 1 (systemd), state S: alive · the message names it: Process 189145 has 6.17 GiB · a Unix zombie keeps only its PID, status and usage; · an orphan is a live process, adopted by init · Take the PID from the message to ps: · a parent of 1 means an orphan. Stop it. · FIVE CAUSES OF ONE CUDA OOM · CANERY.IN
- Alt text: Timeline of an exited child losing its GPU memory while still a zombie, beside a live orphan that keeps 6.17 GiB.
- Long description: The lab started a child that held 6 GiB on the GPU and exited without its parent reaping it. NVML listed it while running and briefly as a zombie at 0.27 s; by 0.40 s it was still a zombie but gone from NVML, and the machine's free memory had risen 6.61 GiB. A process left over from a killed job is different: its parent is PID 1 (systemd), its state is S, it is alive, and the out-of-memory message named it, Process 189145 holding 6.17 GiB. Take the PID from the message to ps; a parent of 1 marks an orphan to stop.
- Keywords: zombie process, orphan process, GPU memory, NVML, PID, out of memory
- Canonical URL: https://canery.in/blogs/five-causes-of-cuda-out-of-memory

### feed-05-outside-pytorch

- File: `assets/social/feed-05-outside-pytorch.png`
- Title: What PyTorch's books can't see
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Memory a process holds outside PyTorch's allocator, measured on the GB10: a 173 MiB lazy context, 943 MiB eager, 548 MiB more for NCCL on one rank, and run 5's library pool at 4.33 GiB
- Technical source: Who else is holding the card?; Figure 8; Worked example run 5; ledger L27, L30, L32
- Visual structure: lockup and counter; serif title; deck; three horizontal bars to one scale; a rule; run 5's outside-PyTorch total in large tangerine type; notes; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · What PyTorch's · books can't see. · The context, NCCL and other libraries' pools · sit in the process but outside the allocator. · one process's GPU memory outside PyTorch, on the GB10 · CUDA context, lazy · 173 MiB · context, eager loading · 943 MiB · + NCCL on one rank · 548 MiB · run 5: a library's 4 GiB pool in the same process · this process − PyTorch's reserved · 4.33 GiB · memory snapshots never see it; cuBLAS workspaces are · not in it: PyTorch 2.15 takes them from its allocator · This process minus allocated and unallocated · is the memory outside PyTorch. · FIVE CAUSES OF ONE CUDA OOM · CANERY.IN
- Alt text: Bars of a process's GPU memory outside PyTorch: a 173 MiB lazy context, 943 MiB eager, 548 MiB for NCCL, and 4.33 GiB in run 5.
- Long description: Measured on an NVIDIA GB10 with PyTorch 2.15.0, the CUDA context held 173 MiB with lazy module loading and 943 MiB with eager loading, and starting NCCL's communicator on one rank added 548 MiB, all outside PyTorch's allocator. In run 5 a library's 4 GiB pool in the same process brought the memory outside PyTorch to 4.33 GiB, which is the message's this-process figure minus PyTorch's reserved memory. Memory snapshots cannot see it; cuBLAS workspaces are not in it, because PyTorch 2.15 takes them from its own allocator.
- Keywords: CUDA context, lazy loading, NCCL, non-PyTorch memory, PyTorch memory snapshot, GPU memory
- Canonical URL: https://canery.in/blogs/five-causes-of-cuda-out-of-memory

### feed-06-empty-cache

- File: `assets/social/feed-06-empty-cache.png`
- Title: empty_cache() can't save the crash
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Calling torch.cuda.empty_cache() and retrying failed in both runs it was tried in, because the allocator had already released every cached segment that was free at the failure
- Technical source: What does the caching allocator do with freed memory?; Limitations; ledger L15, L26
- Visual structure: lockup and counter; serif title; deck; two labelled results, each the amount released and a tangerine line saying the retry failed again; a note on the allocator's release; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · empty_cache() can't · save the crash. · Everything cached and free at the failure, · the allocator had already released. · catch the error, call torch.cuda.empty_cache(), retry · run 1, fragmentation: released · 3.00 GiB · the failed operation's own outputs, freed as it unwound · then the same optimizer step: failed again · run 2, capacity: released · 0 bytes · then the same forward pass: failed again · before it raises, the allocator has already freed every · cached segment that holds no live tensor · It hands cache to other processes; for the · crashed one, the allocator already tried. · FIVE CAUSES OF ONE CUDA OOM · CANERY.IN
- Alt text: Card showing empty_cache() releasing 3.00 GiB and 0 bytes in two failed runs, each retry failing again.
- Long description: In the fragmentation run, empty_cache() after the error released 3.00 GiB, the failed operation's own half-built outputs freed as the error unwound, and the same optimizer step failed again. In the capacity run it released 0 bytes and the same forward pass failed again. Before raising the error, PyTorch's allocator has already freed every cached segment that holds no live tensor, so empty_cache() hands cache to other processes but cannot rescue the process that crashed.
- Keywords: torch.cuda.empty_cache, PyTorch caching allocator, out of memory, retry, GPU memory
- Canonical URL: https://canery.in/blogs/five-causes-of-cuda-out-of-memory

### feed-07-read-in-this-order

- File: `assets/social/feed-07-read-in-this-order.png`
- Title: Read the message in this order
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The decision tree as five ordered questions, each answered by one number from the lab's five runs, with growth checked first
- Technical source: Worked example, Figure 3; The math
- Visual structure: lockup and counter; serif title; deck; a numbered list of five questions, each with its cause and the run's deciding number, the first in tangerine; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · Read the message · in this order. · Five questions, each answered by one number; · the answers are the lab's five runs. · 1 · allocated grows per iteration? · retained graph · +1.55 GiB a batch · 2 · unallocated ≥ the request? · fragmentation · 4.63 GiB vs 256 MiB · 3 · other processes cover it? · another process · 6.17 GiB · 4 · outside PyTorch beyond the context? · outside PyTorch · 4.33 GiB · 5 · none of these · capacity · 23.25 of 23.67 GiB · Growth first: a leak also leaves slivers · that read as fragmentation. · FIVE CAUSES OF ONE CUDA OOM · CANERY.IN
- Alt text: Five ordered questions for an out-of-memory message, each with its cause and the lab run's deciding number.
- Long description: Read an out-of-memory message in this order. First, does allocated memory grow per iteration? That is a retained graph, 1.55 GiB a batch in the lab. Second, is reserved-but-unallocated memory at least the request? That is fragmentation, 4.63 GiB against 256 MiB. Third, do other processes cover the shortfall? Another process, 6.17 GiB. Fourth, does this process hold more outside PyTorch than its context? Memory outside PyTorch, 4.33 GiB. Otherwise it is capacity, 23.25 of 23.67 GiB allowed. Growth comes first because a leak also leaves slivers that read as fragmentation.
- Keywords: decision tree, CUDA out of memory, fragmentation, retained graph, capacity, debugging
- Canonical URL: https://canery.in/blogs/five-causes-of-cuda-out-of-memory

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: Five causes of one CUDA out of memory
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: The article's five causes with one measured number each, and where to read it
- Technical source: Key takeaways; Worked example
- Visual structure: lockup and counter; serif title; deck; five causes, each a heading with its measured number; takeaway; the article URL in tangerine
- Visible-text transcript: Canery.in · 08 / 08 · Five causes of one · CUDA out of memory. · Measured with PyTorch 2.15.0, every message · real, and a lab that reproduces all five. · fragmentation · 4.63 GiB free in 38 pieces, none of 256 MiB · a retained graph · +1.55 GiB a batch without no_grad · another process · an orphan's 6.17 GiB, named in the message · outside PyTorch · context 173 MiB lazy, 943 eager; NCCL +548 MiB · capacity · 23.25 GiB allocated; checkpointing ran the batch · The decision tree, the allocator's rules, · and what each fix does. · READ IT AT CANERY.IN/BLOGS/FIVE-CAUSES-OF-CUDA-OUT-OF-MEMORY
- Alt text: Summary card of five causes of CUDA out-of-memory errors with one measured number each, and the article's address.
- Long description: The article measures five causes of one CUDA out-of-memory error with PyTorch 2.15.0: fragmentation, 4.63 GiB free in 38 pieces and none of 256 MiB; a retained graph, 1.55 GiB a batch without no_grad; another process, an orphan's 6.17 GiB named in the message; memory outside PyTorch, a 173 MiB lazy context or 943 MiB eager and 548 MiB more for NCCL; and capacity, 23.25 GiB allocated until activation checkpointing ran the batch. It covers the decision tree, the allocator's rules and what each fix does, with a lab that reproduces all five.
- Keywords: CUDA out of memory, PyTorch, GPU memory, caching allocator, debugging, NVIDIA
- Canonical URL: https://canery.in/blogs/five-causes-of-cuda-out-of-memory
