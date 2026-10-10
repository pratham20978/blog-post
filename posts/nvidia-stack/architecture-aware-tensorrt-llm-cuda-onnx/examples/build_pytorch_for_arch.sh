#!/usr/bin/env bash
set -euo pipefail

: "${PYTORCH_SOURCE:?Set PYTORCH_SOURCE to a pinned PyTorch checkout}"

TARGET_CC="${TARGET_CC:-12.1}"
MAX_BUILD_JOBS="${MAX_BUILD_JOBS:-4}"
BUILD_MODE="${BUILD_MODE:-editable}"

if [[ ! -f "${PYTORCH_SOURCE}/setup.py" ]]; then
    printf 'No PyTorch setup.py found under %s\n' "$PYTORCH_SOURCE" >&2
    exit 2
fi

if ! command -v nvcc >/dev/null 2>&1; then
    printf 'nvcc is required and was not found on PATH\n' >&2
    exit 2
fi

target_suffix="${TARGET_CC/.}"
if ! nvcc --list-gpu-arch | grep -qx "compute_${target_suffix}"; then
    printf 'Selected nvcc does not list compute_%s\n' "$target_suffix" >&2
    exit 2
fi

if ! grep -q "'${TARGET_CC}'" \
    "${PYTORCH_SOURCE}/torch/utils/cpp_extension.py"; then
    printf 'Pinned PyTorch source does not list target %s\n' "$TARGET_CC" >&2
    exit 2
fi

export TORCH_CUDA_ARCH_LIST="$TARGET_CC"
export CMAKE_BUILD_PARALLEL_LEVEL="$MAX_BUILD_JOBS"
export MAX_JOBS="$MAX_BUILD_JOBS"
export CMAKE_PREFIX_PATH="${VIRTUAL_ENV:-${CONDA_PREFIX:-}}${CMAKE_PREFIX_PATH:+:${CMAKE_PREFIX_PATH}}"

cd "$PYTORCH_SOURCE"
git rev-parse HEAD
printf 'TORCH_CUDA_ARCH_LIST=%s\n' "$TORCH_CUDA_ARCH_LIST"
printf 'BUILD_MODE=%s\n' "$BUILD_MODE"

case "$BUILD_MODE" in
    editable)
        python -m pip install --no-build-isolation -v -e .
        ;;
    wheel)
        # setup.py bdist_wheel is available in current PyTorch sources; verify
        # the packaging command against the README/CI of the pinned tag.
        python setup.py bdist_wheel
        ;;
    *)
        printf 'BUILD_MODE must be editable or wheel\n' >&2
        exit 2
        ;;
esac
