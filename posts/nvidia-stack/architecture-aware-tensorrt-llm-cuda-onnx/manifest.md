# Asset manifest — architecture-aware-tensorrt-llm-cuda-onnx

The editable HTML and SVG figure files, and the 2x PNG renders, are in `assets/` (regenerate with `python3 _figs_a.py && python3 _figs_b.py && python3 _cover.py`).

| Placeholder | File | Suggested path | Alt text |
|---|---|---|---|
| LAB_01 | `examples/README.md` | `labs/architecture-aware-tensorrt-llm-cuda-onnx/README.md` | Lab prerequisites, layout, and run order |
| LAB_02 | `examples/audit_stack.sh` | `labs/architecture-aware-tensorrt-llm-cuda-onnx/audit_stack.sh` | Host, driver, compiler, and environment audit |
| LAB_03 | `examples/audit_torch.py` | `labs/architecture-aware-tensorrt-llm-cuda-onnx/audit_torch.py` | PyTorch and synchronized CUDA audit |
| LAB_04 | `examples/benchmark-report.md` | `labs/architecture-aware-tensorrt-llm-cuda-onnx/benchmark-report.md` | Reproducible benchmark report template |
| LAB_05 | `examples/benchmark.sh` | `labs/architecture-aware-tensorrt-llm-cuda-onnx/benchmark.sh` | AIperf benchmark harness |
| LAB_06 | `examples/build_pytorch_for_arch.sh` | `labs/architecture-aware-tensorrt-llm-cuda-onnx/build_pytorch_for_arch.sh` | Architecture-gated PyTorch build driver |
| LAB_07 | `examples/cuda_probe/CMakeLists.txt` | `labs/architecture-aware-tensorrt-llm-cuda-onnx/cuda_probe/CMakeLists.txt` | CUDA probe build configuration |
| LAB_08 | `examples/cuda_probe/probe.cu` | `labs/architecture-aware-tensorrt-llm-cuda-onnx/cuda_probe/probe.cu` | CUDA architecture kernel probe |
| LAB_09 | `examples/export_onnx.py` | `labs/architecture-aware-tensorrt-llm-cuda-onnx/export_onnx.py` | Dynamic ONNX exporter and checker |
| LAB_10 | `examples/extension_probe/binding.cpp` | `labs/architecture-aware-tensorrt-llm-cuda-onnx/extension_probe/binding.cpp` | Python binding for the extension probe |
| LAB_11 | `examples/extension_probe/kernel.cu` | `labs/architecture-aware-tensorrt-llm-cuda-onnx/extension_probe/kernel.cu` | CUDA extension kernel |
| LAB_12 | `examples/extension_probe/setup.py` | `labs/architecture-aware-tensorrt-llm-cuda-onnx/extension_probe/setup.py` | Extension build definition |
| LAB_13 | `examples/extension_probe/test_extension.py` | `labs/architecture-aware-tensorrt-llm-cuda-onnx/extension_probe/test_extension.py` | Extension runtime validation |
| LAB_14 | `examples/inspect_model.py` | `labs/architecture-aware-tensorrt-llm-cuda-onnx/inspect_model.py` | Immutable model configuration inspection |
| LAB_15 | `examples/run_onnx.py` | `labs/architecture-aware-tensorrt-llm-cuda-onnx/run_onnx.py` | ONNX Runtime provider probe |
| LAB_16 | `examples/run_trtllm.py` | `labs/architecture-aware-tensorrt-llm-cuda-onnx/run_trtllm.py` | Minimal TensorRT-LLM generation |
| COVER | `cover.png` | `blog/architecture-aware-tensorrt-llm-cuda-onnx/cover-v1.png` | Title card beside a six-layer compatibility stack motif with the code-images layer highlighted |
| FIG_01 | `fig-01-compatibility-stack.png` | `blog/architecture-aware-tensorrt-llm-cuda-onnx/fig-01-v1.png` | Six-layer compatibility stack from host and GPU through compiler, PyTorch, runtime, and model workload |
| FIG_02 | `fig-02-capability-vs-toolkit.png` | `blog/architecture-aware-tensorrt-llm-cuda-onnx/fig-02-v1.png` | Separate axes compare GPU compute capabilities for T4 and GB10 with CUDA Toolkit software releases |
| FIG_03 | `fig-03-two-hosts.png` | `blog/architecture-aware-tensorrt-llm-cuda-onnx/fig-03-v1.png` | Side-by-side T4 and GB10 cases showing a validation gap versus a binary code-coverage gap |
| FIG_04 | `fig-04-code-image-selection.png` | `blog/architecture-aware-tensorrt-llm-cuda-onnx/fig-04-v1.png` | Decision flow choosing an exact or compatible cubin, a compatible PTX JIT path, or no kernel image |
| FIG_05 | `fig-05-audit-decision-tree.png` | `blog/architecture-aware-tensorrt-llm-cuda-onnx/fig-05-v1.png` | Audit decision tree testing GPU visibility, compiler target, PyTorch core, extension, and model support in order |
| FIG_06 | `fig-06-pytorch-compatibility-test.png` | `blog/architecture-aware-tensorrt-llm-cuda-onnx/fig-06-v1.png` | Four evidence inputs combine device capability, binary inventory, warnings, and a synchronized core operation |
| FIG_07 | `fig-07-cuda-compilation-pipeline.png` | `blog/architecture-aware-tensorrt-llm-cuda-onnx/fig-07-v1.png` | CUDA source compiles into native cubin and virtual PTX images that are packaged in one fatbinary |
| FIG_08 | `fig-08-cmake-target-map.png` | `blog/architecture-aware-tensorrt-llm-cuda-onnx/fig-08-v1.png` | CMake CUDA architecture values mapped to native cubin, virtual PTX, and host-native output choices |
| FIG_09 | `fig-09-evidence-matrix.png` | `blog/architecture-aware-tensorrt-llm-cuda-onnx/fig-09-v1.png` | Eight evidence layers with their authoritative observation and which rows three repairs force you to re-collect |
| FIG_10 | `fig-10-failure-phase-ownership.png` | `blog/architecture-aware-tensorrt-llm-cuda-onnx/fig-10-v1.png` | Five failure phases on a timeline, each mapped to the artifact that owns its repair and the wrong reflex it triggers |
| FIG_11 | `fig-11-repair-ladder.png` | `blog/architecture-aware-tensorrt-llm-cuda-onnx/fig-11-v1.png` | Repair ladder prioritizing wheel replacement, one extension rebuild, PyTorch rebuild, then runtime changes |
| FIG_12 | `fig-12-pytorch-build-pipeline.png` | `blog/architecture-aware-tensorrt-llm-cuda-onnx/fig-12-v1.png` | Six-stage PyTorch source-build pipeline from pinned source and toolchain to fresh-environment verification |
| FIG_13 | `fig-13-transformer-kv-cache.png` | `blog/architecture-aware-tensorrt-llm-cuda-onnx/fig-13-v1.png` | Transformer prefill creates a paged KV cache that decode steps reuse and extend one token at a time |
| FIG_14 | `fig-14-model-support-gates.png` | `blog/architecture-aware-tensorrt-llm-cuda-onnx/fig-14-v1.png` | Four sequential serving gates cover CUDA execution, model adapter, feature precision, and memory shapes |
| FIG_15 | `fig-15-deployment-fork.png` | `blog/architecture-aware-tensorrt-llm-cuda-onnx/fig-15-v1.png` | Hugging Face checkpoint branches directly to TensorRT-LLM or through ONNX to TensorRT and ONNX Runtime |
| FIG_16 | `fig-16-validation-vs-execution.png` | `blog/architecture-aware-tensorrt-llm-cuda-onnx/fig-16-v1.png` | Two-axis matrix separates official validation from observed execution, including an unlisted working stack |
| FIG_17 | `fig-17-kv-memory-budget.png` | `blog/architecture-aware-tensorrt-llm-cuda-onnx/fig-17-v1.png` | KV cache bars for one, four, and sixteen resident sequences measured against the headroom left by the fixed memory terms |
| FIG_18 | `fig-18-benchmark-timeline.png` | `blog/architecture-aware-tensorrt-llm-cuda-onnx/fig-18-v1.png` | Request timeline marks time to first token, inter-token gaps, completion, and end-to-end latency |

Upload each PNG to its versioned suggested path. Then write the resulting URLs to `urls.txt`, one per line in manifest order, and run:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py \
  posts/nvidia-stack/architecture-aware-tensorrt-llm-cuda-onnx/ \
  posts/nvidia-stack/architecture-aware-tensorrt-llm-cuda-onnx/urls.txt
```

Use a new `-vN` path when an image changes; do not overwrite a previously cached object.
