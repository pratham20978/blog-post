# Outline — Why Your GPU Is Idle at 100% Utilization

**Series:** nvidia-stack, part 3 · **Tier:** L3 · **Difficulty:** intermediate
**Budget:** ~6,000 words · **Figures:** 10 · **Lab:** Tier A model + Tier B harness (no GPU here)

## The spine

A GPU can be idle in two directions, and `nvidia-smi` sees only one of them, coarsely.

| Direction | What is idle | What `nvidia-smi` utilization says | What finds it |
|---|---|---|---|
| **Space** | most SMs, while one narrow kernel is resident | 100% — a kernel was executing | DCGM SM Activity, Nsight Systems *SMs Active* (definitions only; part 5 owns the workflow) |
| **Time** | the whole GPU, while the host has not sent the next kernel | a lower number, averaged over 1/6–1 s | CUDA events against a host timer — this part |

The title's claim is the first row and is answered in Insights and *The problem*, from NVIDIA's
own definition. The body is the second row, because the reader's actual question is "where did
the time go", and on a slow job the answer is usually the host: the execution model is
asynchronous, a sync point drains the queue, and a host timer bills the wait to the wrong line.
The two rows meet at the end of the math section: remove the host-side time and the step reads
100% — the point at which `nvidia-smi` stops being able to tell you anything.

**The rule the post exists to deliver:** a sync point costs nothing itself; it costs the overlap
it destroys. Formally, it turns one `max(host, GPU)` into a sum of per-segment maxes.

## Worked example (model, not measurement)

One stream, one training step. Round inputs, followed by hand, produced by `lab/queue_model.py`:

| Phase | Kernels | Host per launch | GPU per kernel | Host total | GPU total |
|---|---|---|---|---|---|
| forward | 40 | 20 µs | 100 µs | 0.8 ms | 4.0 ms |
| backward | 80 | 20 µs | 100 µs | 1.6 ms | 8.0 ms |
| `loss.item()` | sync | — | — | — | — |
| optimizer (for-loop) | 1,000 | 20 µs | 3 µs | 20.0 ms | 3.0 ms |

| Readout | forward | backward | `loss.item()` | optimizer | step |
|---|---|---|---|---|---|
| host timer | 0.8 | 1.6 | **9.6** | 20.0 | 32.0 |
| CUDA events | 4.0 | 8.0 | **0.0** | 20.0 | 32.0 |
| kernels actually ran | 4.0 | 8.0 | 0.0 | 3.0 | 15.0 |

GPU idle 17.0 of 32.0 ms = **53%** — more than half the wall clock is host-side. By
`nvidia-smi`'s definition a window of such steps reads 15.0 / 32.0 = **47%**.

Fixes, steady state: drop the mid-step sync → **22.4 ms**, 67%; also issue the optimizer as 10
launches (or capture the step as one graph) → **15.0 ms**, 100%. A 20-step loop timed with no
final sync then reports **2.6 ms/step** (0.02 as a graph) against a true 15.0 — the second
wrong answer, and it only exists once the step is fixed.

The inputs are a model's, labelled as such in the prose and the captions. The 20 µs launch cost
is a round number above the ~2.5 µs raw CUDA launch measured on a V100 (L-row) because a
framework adds its own per-op scheduling on top (Nimble's list, L-row). The Tier B script
measures the real ones and ships an empty schema until it is run.

## Sections and budget

| Section | Words | Figure | The one thing |
|---|---|---|---|
| Insights + who this is for | 150 | COVER | 100% means a kernel was executing; the slow part is usually on the host |
| Why this matters | 220 | — | the dashboard number and the slow job both tell the truth |
| The problem: a clock, not a gauge | 480 | FIG_01 | time-based, any kernel, 1/6–1 s; one narrow kernel reads 100% |
| Worked example: one training step, timed twice | 950 | FIG_02, FIG_03 | the host timer bills 9.6 ms to a line that did no work |
| Intuition: two clocks and a queue | 520 | FIG_04 | the queue depth tells you who is waiting for whom |
| What is a stream, and what does an event time? | 560 | FIG_05, FIG_06 | an event times the stream's clock, gaps included |
| Host-side sync points | 620 | FIG_07 | the catalogue, and how to make PyTorch name them |
| What does a kernel launch cost? | 480 | FIG_08 | microseconds, hidden only behind a longer kernel |
| What do CUDA Graphs remove, and what do they not? | 620 | FIG_09 | one launch for many; nothing about kernel time or syncs |
| The math: a sync point turns one max into a sum | 480 | FIG_10 | the recurrence, then 32.0 → 22.4 → 15.0 |
| Implementation: timing a step without lying | 420 | — | events per phase, sync-debug mode, a captured step |
| Limitations and common mistakes | 380 | — | synchronize-everything, launch-blocking, loops without a final sync |
| Key takeaways + references | 150 | — | |

`## Host-side sync points` is a **fixed heading**: part 5 links to `#host-side-sync-points`.

## Figure plan

Every route settled by the gate in `blog-visuals/references/visual-taxonomy.md`. Model-derived
figures import `lab/queue_model.py` so the drawn numbers cannot drift from the prose.

| # | Shows | Route | Why |
|---|---|---|---|
| FIG_01 | four sample windows: what `nvidia-smi` reads vs DCGM SM Activity (one narrow kernel, N/5 blocks, N blocks for 1/5 of the window, N blocks throughout) | placed | Q4 — small multiples with time and SM coverage to scale; the value is the mismatch between two numbers per panel |
| FIG_02 | the step as two lanes, host and GPU, 0–32 ms to scale, with the wait and the idle gaps | placed | Q4 — a to-scale timeline; the reader must see the empty GPU lane |
| FIG_03 | host-timer readout against event readout per phase, with the 9.6 ms moved | placed | Q4 — paired bars to scale; the transfer between two rows is the figure |
| FIG_04 | queue depth over the step, from the model | plot | Q4 — a step curve computed from the recurrence; geometry, not boxes |
| FIG_05 | two streams, an event, and a device-side wait | placed | Q5 — six nodes on two lanes, no crossings; order in time carries it |
| FIG_06 | the legacy default stream serialising two blocking streams, against a non-blocking pair | placed | Q4 — two small timelines side by side, to scale |
| FIG_07 | the sync-point catalogue: call, what it waits for, where PyTorch triggers it | placed | Q4 — a grid of real API names and conditions |
| FIG_08 | Gray's V100 measurement: 2.9 µs kernel, 9.6 / 3.8 / 3.4 µs per kernel | chart | Q1 — measured numbers in the ledger, with their setup |
| FIG_09 | what a graph replay removes and what survives, eager lane vs graph lane | placed | Q4 — two to-scale lanes with the surviving costs labelled |
| FIG_10 | the three versions of the step, 32.0 / 22.4 / 15.0 ms, with utilization | placed | Q4 — small multiples to one scale; the shrinking host lane is the argument |

No paper figure passes the source gate: Paszke et al. Figure 1 is the closest (a ResNet-50 CPU/GPU
trace), but arXiv's non-exclusive licence grants no reuse, and our own worked example carries
the same point with numbers the reader can check. Recorded in the ledger as `do not reuse`.

Budget check: 10 figures at ~6,000 words is one per 600, inside L3's band.

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| GPU utilization (`nvidia-smi`) | The problem | NVML's time fraction: some kernel executing, over 1/6–1 s | it is the number on every dashboard | when deciding whether the queue ever ran dry |
| streaming multiprocessor (SM) | The problem | the GPU's unit of execution; a kernel's blocks are spread over SMs | "busy" in space means SMs, not time | when one kernel is narrower than the chip |
| SM Activity (DCGM) | The problem | fraction of time at least one warp is active per SM, averaged | the spatial number `nvidia-smi` lacks | when utilization reads 100% and the job is slow |
| kernel launch | Worked example | the host call that enqueues one GPU function | each costs host time before the GPU sees it | when kernels are short |
| synchronization point | Worked example | a call that blocks the host until queued GPU work finishes | it drains the queue | whenever a value crosses back to Python |
| CUDA stream | Streams section | an in-order work queue on the device | the unit of ordering and concurrency | when overlapping work or timing it |
| CUDA event | Worked example (used), Streams section (defined) | a marker in a stream, time-stamped when the GPU reaches it | it reads the GPU's clock, not the host's | whenever you time GPU work |
| legacy default stream | Streams section | stream 0 with implicit synchronisation | a hidden serialiser | when mixing default and created streams |
| launch overhead | Launch section | host + driver + GPU cost per kernel | exposed when kernels are shorter than launches | small batches, many small ops |
| CUDA Graph | Graphs section | a captured DAG of GPU work, instantiated once, launched many times | one launch replaces many | when CPU-limited and graph-safe |
| stream capture | Graphs section | recording a stream's work into a graph | how PyTorch builds graphs | when the step is static |

## Boundaries

- **Assumes** part 1's layer map, recapped in at most three sentences, linked by anchor
  (`#the-problem-five-different-things-are-called-cuda`). Part 2 is not a prerequisite.
- **Does not touch** the profiler workflow (Nsight Systems/Compute usage, roofline) — part 5.
  Nsight rows and DCGM fields are *defined*, never walked through.
- **Does not touch** kernel-internal memory behaviour, occupancy tuning or coalescing — part 8.
  "Why are the SMs idle inside a resident kernel" is named and handed off.
- **Does not touch** the caching allocator beyond the one sentence that `cudaFree` blocks — part 4.
- **Hands off** the two-clock timeline that parts 4 and 5 read.
