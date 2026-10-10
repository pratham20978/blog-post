#!/usr/bin/env bash
set -u

heading() {
    printf '\n[%s]\n' "$1"
}

run_if_present() {
    local program="$1"
    shift
    if command -v "$program" >/dev/null 2>&1; then
        "$program" "$@" || true
    else
        printf '%s: not found\n' "$program"
    fi
}

heading "host"
uname -a
printf 'machine=%s\n' "$(uname -m)"
if [[ -r /etc/os-release ]]; then
    sed -n '1,12p' /etc/os-release
fi

heading "driver and visible GPUs"
if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi --query-gpu=index,name,uuid,driver_version,compute_cap,memory.total \
        --format=csv,noheader || nvidia-smi
else
    printf 'nvidia-smi: not found\n'
fi

heading "CUDA Toolkit selected by PATH"
if command -v nvcc >/dev/null 2>&1; then
    printf 'nvcc=%s\n' "$(command -v nvcc)"
    nvcc --version
    printf '\nvirtual targets:\n'
    nvcc --list-gpu-arch || true
    printf '\nreal targets:\n'
    nvcc --list-gpu-code || true
else
    printf 'nvcc: not found\n'
fi

heading "build and runtime tools"
run_if_present cmake --version
run_if_present ninja --version
run_if_present python3 --version
run_if_present docker --version

heading "relevant environment"
printf 'CUDA_HOME=%s\n' "${CUDA_HOME-<unset>}"
printf 'CUDAToolkit_ROOT=%s\n' "${CUDAToolkit_ROOT-<unset>}"
printf 'TORCH_CUDA_ARCH_LIST=%s\n' "${TORCH_CUDA_ARCH_LIST-<unset>}"
printf 'CUDA_VISIBLE_DEVICES=%s\n' "${CUDA_VISIBLE_DEVICES-<unset>}"
