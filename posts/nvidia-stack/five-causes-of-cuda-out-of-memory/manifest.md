# Asset manifest — five-causes-of-cuda-out-of-memory

Series `nvidia-stack`, part 4. **Status: local draft assets ready for upload.** Upload the ten PNGs and the
seven lab files to the public `media` bucket under the object keys below, write the resulting URLs to
`urls.txt` in table order (COVER, FIG_01–FIG_09, then LAB_01–LAB_07), then run `fill_urls.py`. Upload the
lab zip separately, to the bucket root (see **Lab files**). Nothing has been published, so every key is new;
the names carry the slug because the bucket is flat.

Every figure is our own analysis. `assets/_figs.py` draws figures 1, 2 and 5–9 from the lab's
`captures.json` and asserts the numbers the article quotes before it draws; it also writes the `.mmd`
sources of figures 3 and 4 from the same data, which `assets/_mermaid.py` lays out with Mermaid 11
(edge labels opaque). The cover is `assets/_cover.py`. Re-run `python3 _figs.py <nn>` or `python3 _cover.py`
inside `assets/` to rebuild any of them; the `.html`, `.svg` and 2× `.png` are emitted together.

**Route gate.** The `source` route was checked first (ledger, **Figure candidates**): GMLake's Figure 1 has no
reuse licence, and Figure 5 draws this run's own segments instead; the PyTorch devlog's layouts are text
dumps. Figures 2 and 7–9 are measured series (Q1, `chart`); Figure 5 draws the measured snapshot to scale
(Q1, `plot`); Figure 1 is the run's verbatim message (Q2, `capture`); Figures 3 and 4 are graphs of
decisions with more than nine nodes or converging paths (Q3, `mermaid`); Figure 6 is address ranges and
pages, whose value is the proportion (Q4, `placed`).

**Checks the gate cannot make, and their results.** Every PNG was opened and read. Fixed before shipping:
Figure 2's labels ran off the canvas and the baseline carried the outline meant for each run's deciding
segment; Figure 5's request annotation sat on the grid of live segments and its last temporary was cut
off; Figure 6 drew its "separate" segments overlapping; Figure 9's labels sat on their lines; the cover's
motif touched the title. `_overlap.py` reports 0 issues on figures 1, 2 and 5–9; its hits on figures 3 and 4
are the known Mermaid edge-label false positive (every label measured at one origin), and
`lint_visuals.py`'s arrow reports on those two are the same transform blind spot: both PNGs show every
edge landing on its node.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-five-causes-of-cuda-out-of-memory.png | placed | template cover in the series' Part 3 layout, built by `_cover.py`: Figure 5 reduced to its argument, the request beside the 37 tails, tangerine on the request and the tails | — | — | cover-five-causes-of-cuda-out-of-memory.png | A 256 MiB request above 37 memory segments, each a live block beside a free tail too small to hold it |
| FIG_01 | assets/fig-01-message-anatomy-five-causes-of-cuda-out-of-memory.png | capture | Q2: the fragmentation run's own message, verbatim, with its six numbers annotated | — | — | fig-01-message-anatomy-five-causes-of-cuda-out-of-memory.png | The fragmentation run's message, each of its numbers labelled with the instrument behind it and the cause it can reveal |
| FIG_02 | assets/fig-02-five-runs-one-card-five-causes-of-cuda-out-of-memory.png | chart | Q1: each run's measured ledger stacked on one 24 GiB scale | — | — | fig-02-five-runs-one-card-five-causes-of-cuda-out-of-memory.png | Six bars on one 24 GiB scale, a baseline and five failed runs, each split by who held the memory, the request past the edge |
| FIG_03 | assets/fig-03-decision-tree-five-causes-of-cuda-out-of-memory.png | mermaid | Q3: 11 nodes, a chain of five questions each with a branch; laid out left to right | — | — | fig-03-decision-tree-five-causes-of-cuda-out-of-memory.png | Decision tree: growth means a retained graph, then unallocated at least the request means fragmentation, then other holders, then capacity |
| FIG_04 | assets/fig-04-allocator-path-five-causes-of-cuda-out-of-memory.png | mermaid | Q3: four paths converge on the split node and two retry loops cross the chain | — | — | fig-04-allocator-path-five-causes-of-cuda-out-of-memory.png | PyTorch's allocator path: round, take the smallest free block and split it, else cudaMalloc, else free cached blocks, retry, raise |
| FIG_05 | assets/fig-05-slivers-five-causes-of-cuda-out-of-memory.png | plot | Q1: the allocator snapshot's 77 segments drawn to scale | — | — | fig-05-slivers-five-causes-of-cuda-out-of-memory.png | Run 1's segments to scale: 37 of 384 MiB, each a live 256 MiB tensor beside a free 128 MiB tail, and a 256 MiB request |
| FIG_06 | assets/fig-06-expandable-segments-five-causes-of-cuda-out-of-memory.png | placed | Q4: address ranges and physical pages, blocks in proportion | — | — | fig-06-expandable-segments-five-causes-of-cuda-out-of-memory.png | Separate cudaMalloc segments whose free tails cannot merge, beside one expandable segment whose free space merges at its end |
| FIG_07 | assets/fig-07-retained-graph-five-causes-of-cuda-out-of-memory.png | chart | Q1: measured allocated memory per batch, with and without no_grad | — | — | fig-07-retained-graph-five-causes-of-cuda-out-of-memory.png | Allocated memory per evaluation batch: rising 1.55 GiB a batch from 12.00 to 22.83 GiB and failing, or flat at 12.00 with no_grad |
| FIG_08 | assets/fig-08-outside-pytorch-five-causes-of-cuda-out-of-memory.png | chart | Q1: measured memory outside PyTorch, stage by stage, lazy and eager | — | — | fig-08-outside-pytorch-five-causes-of-cuda-out-of-memory.png | Memory one process holds outside PyTorch: a 173 MiB context with lazy loading, 943 MiB eager, and 892 MiB with NCCL on one rank |
| FIG_09 | assets/fig-09-unified-memory-five-causes-of-cuda-out-of-memory.png | chart | Q1: measured CUDA free, MemFree and MemAvailable at three moments | — | — | fig-09-unified-memory-five-causes-of-cuda-out-of-memory.png | On the GB10, CUDA free and MemFree fall together from 104.25 to 96.22 GiB under an 8 GiB CPU tensor; MemAvailable stays higher |

## Lab files

**Lab grade:** G3 · needs one NVIDIA GPU (this series' Tier B), captured on an NVIDIA GB10 on 2026-10-30;
`diagnose.py` is G1. E1 and E2 run without a GPU from `captures.json`; E3 and E4 need one.

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/five-causes-of-cuda-out-of-memory/README.md` | grade, what was executed, the provenance line, run order, the E1–E4 exercises with answers, cleanup |
| LAB_02 | `lab/oom_lab.py` | `labs/five-causes-of-cuda-out-of-memory/oom_lab.py` | the GPU harness: baseline, five failures, their fixes, the measurements, the E4 mystery faults |
| LAB_03 | `lab/diagnose.py` | `labs/five-causes-of-cuda-out-of-memory/diagnose.py` | the decision tree for any message or captures file, standard library only |
| LAB_04 | `lab/captures.json` | `labs/five-causes-of-cuda-out-of-memory/captures.json` | the run the article quotes |
| LAB_05 | `lab/expected-output.txt` | `labs/five-causes-of-cuda-out-of-memory/expected-output.txt` | that run's console output |
| LAB_06 | `lab/requirements.txt` | `labs/five-causes-of-cuda-out-of-memory/requirements.txt` | the pinned torch and numpy versions |
| LAB_07 | `lab/notebook.ipynb` | `labs/five-causes-of-cuda-out-of-memory/notebook.ipynb` | the README with runnable cells, built by build_lab_notebook.py |
| ARCHIVE | `lab-five-causes-of-cuda-out-of-memory.zip` | `lab-five-causes-of-cuda-out-of-memory.zip` (bucket root) | every lab file in one zip; its final URL is already written in `blog.md` |

Content types: `README.md` text/markdown; `oom_lab.py` text/x-python; `diagnose.py` text/x-python; `captures.json` application/json; `expected-output.txt` text/plain; `requirements.txt` text/plain; `notebook.ipynb` application/x-ipynb+json. Set `Content-Disposition: attachment` on the lab objects so the article links
download rather than render.

```bash
python3 .claude/blog-forge/scripts/fill_urls.py \
  posts/nvidia-stack/five-causes-of-cuda-out-of-memory/ \
  posts/nvidia-stack/five-causes-of-cuda-out-of-memory/urls.txt
```

## Series links to add

| Earlier post | Status on 2026-10-30 | Where it is named in `blog.md` |
|---|---|---|
| Part 3, *Why Your GPU Is Idle at 100% Utilization* | not live (404) | "What does the caching allocator do with freed memory?", first paragraph: "as part 3 of this series, *Why Your GPU Is Idle at 100% Utilization*, showed" |

Later parts are "later in this series", with no number, title or link (Limitations: serving capacity).

## Owner actions

- Upload, fill URLs, then run `validate_post.py --publish`.
- Publish Part 3 before or with this part: it is this part's one prerequisite.
- The social cards in `assets/social/` are not uploaded through this manifest; `social.md` is their
  publishing sheet.
