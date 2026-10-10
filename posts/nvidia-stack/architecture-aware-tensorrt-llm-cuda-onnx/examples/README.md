# Examples

These files accompany the article. They are diagnostic examples, not universal
install scripts. Pin every framework/model revision before using the results in
a benchmark or support claim.

## Static checks

```bash
bash -n audit_stack.sh benchmark.sh build_pytorch_for_arch.sh
python -m py_compile audit_torch.py inspect_model.py run_trtllm.py \
  export_onnx.py run_onnx.py extension_probe/setup.py \
  extension_probe/test_extension.py
```

## GPU checks

```bash
bash audit_stack.sh
python audit_torch.py

cmake -S cuda_probe -B cuda_probe/build -G Ninja -DCUDA_TARGETS=75-real
cmake --build cuda_probe/build
./cuda_probe/build/cuda_arch_probe
```

Use `-DCUDA_TARGETS=121-real` only when the selected `nvcc --list-gpu-code`
contains `sm_121`. A direct `sm_120` or family/virtual target may already be
compatible with a 12.1 device, so do not rebuild based on string inequality.

To rebuild only the sample PyTorch extension:

```bash
cd extension_probe
TORCH_CUDA_ARCH_LIST="7.5" python -m pip install -v .
python test_extension.py
```

Change `7.5` to `12.1` only after verifying the compiler and installed
PyTorch extension tooling recognize it.
