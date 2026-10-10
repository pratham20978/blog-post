# Asset manifest — what-the-nvidia-stack-actually-is

Each figure keeps an editable `.html` in `assets/` beside its `.svg` and 2x `.png`; the `.html`
is the source of truth for a `placed` figure and is what to open for a correction. The cover is
rebuilt with `python3 _cover.py`.

> **Note.** The Python generator that originally emitted figures 1–7 (`assets/_figs.py`) was
> overwritten in a later session and is not recoverable. The `.html`, `.svg` and `.png` for every
> figure survive intact and remain the editable sources the handoff contract requires, so a
> correction is an edit to the `.html` plus a re-export — not a redraw.

Every figure is routed **placed**: the content is structure under nine nodes — layer stacks,
a ruled trace, a coverage matrix, a small dependency graph — which diagram-design hand-places.
None is graph-shaped enough to need Mermaid's layout engine, and none plots measured data, so
neither the `mermaid` nor the `chart` route applies. No paper figure is reused, so the `source`
route and its rights record do not arise.

| Placeholder | File | Route | Why | Suggested path | Alt text |
|---|---|---|---|---|---|
| COVER | `cover.png` | placed | template cover, hand-placed from the post's own layer motif | `blog/what-the-nvidia-stack-actually-is/cover-v1.png` | Title card beside a seven-layer stack motif with the bottom two layers highlighted as host-supplied |
| FIG_01 | `fig-01-layer-map.png` | placed | seven ruled rows with three columns; a table-shaped layout, not a graph | `blog/what-the-nvidia-stack-actually-is/fig-01-v1.png` | Seven stacked layers from kernel modules up to serving products, each row naming its file on disk and the product that ships it, with the bottom two marked host-only |
| FIG_02 | `fig-02-traced-call.png` | placed | a linear nine-step trace; ordering is the content, so hand placement is exact | `blog/what-the-nvidia-stack-actually-is/fig-02-v1.png` | Nine numbered steps tracing a PyTorch matrix multiply down to a kernel-module call, each step labelled with the artifact that owns it and step seven marked as the vendor boundary |
| FIG_03 | `fig-03-supply-channels.png` | placed | a six-by-three coverage matrix of ticks and crosses | `blog/what-the-nvidia-stack-actually-is/fig-03-v1.png` | A matrix of six stack layers against three supply channels, showing that only the driver installer covers the bottom two layers |
| FIG_04 | `fig-04-driver-contents.png` | placed | two parallel columns of five and four boxes, under the nine-node ceiling | `blog/what-the-nvidia-stack-actually-is/fig-04-v1.png` | Five NVIDIA kernel modules on the left with two marked as the compute path, and four driver-installed user-space libraries on the right with libcuda.so.1 highlighted |
| FIG_05 | `fig-05-toolkit-versions.png` | placed | a ruled two-column table; the point is the spread down one column | `blog/what-the-nvidia-stack-actually-is/fig-05-v1.png` | Nine CUDA Toolkit component wheels listed with their own version numbers, ranging from 10.4.0.35 to 13.1.1.3 inside a single 13.0.3 release |
| FIG_06 | `fig-06-cuda-x-label.png` | placed | containment: a dashed label drawn over two groups of boxes | `blog/what-the-nvidia-stack-actually-is/fig-06-v1.png` | A dashed CUDA-X boundary drawn over two rows of libraries, those inside the Toolkit and those shipped separately, with an arrow from cuDNN to cuBLAS |
| FIG_07 | `fig-07-resolved-graph.png` | placed | nine nodes in two containers with no crossing edges | `blog/what-the-nvidia-stack-actually-is/fig-07-v1.png` | The resolved dependency graph of pip install torch inside a site-packages box, with libcuda.so.1 and the kernel module drawn outside it in a host box |
| LAB_01 | `lab/README.md` | — | — | `labs/what-the-nvidia-stack-actually-is/README.md` | Lab prerequisites, run order, expected output and caveats |
| LAB_02 | `lab/wheelio.py` | — | — | `labs/what-the-nvidia-stack-actually-is/wheelio.py` | Shared helpers: PyPI metadata, an HTTP Range file object, and an ELF64 dynamic-section reader |
| LAB_03 | `lab/inspect_wheel.py` | — | — | `labs/what-the-nvidia-stack-actually-is/inspect_wheel.py` | Lists a wheel's contents and every library's SONAME, DT_NEEDED and DT_RPATH without installing it |
| LAB_04 | `lab/resolve_stack.py` | — | — | `labs/what-the-nvidia-stack-actually-is/resolve_stack.py` | Maps every requested shared library to the wheel that provides it, or to the host driver |
| LAB_05 | `lab/expected-output.txt` | — | — | `labs/what-the-nvidia-stack-actually-is/expected-output.txt` | Captured output of both scripts, dated, for diffing against drift |

Upload each PNG and each lab file to its suggested path in the public MinIO `media` bucket. Then
write the resulting URLs to `urls.txt`, one per line in manifest order, and run:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py \
  posts/nvidia-stack/what-the-nvidia-stack-actually-is/ \
  posts/nvidia-stack/what-the-nvidia-stack-actually-is/urls.txt
```

Set `Content-Type: text/x-python` on the `.py` lab objects and
`Content-Disposition: attachment` on all five lab objects so the article links download rather
than render.
