#!/usr/bin/env python3
"""Print PyTorch build metadata and prove CUDA with a synchronized core op."""

from __future__ import annotations

import json
import platform
import sys
import warnings

import torch


def cxx11_abi() -> bool | str:
    probe = getattr(torch, "compiled_with_cxx11_abi", None)
    return probe() if callable(probe) else "unavailable"


report: dict[str, object] = {
    "python": sys.version.split()[0],
    "platform": platform.platform(),
    "machine": platform.machine(),
    "torch": torch.__version__,
    "torch_cuda_build": torch.version.cuda,
    "cxx11_abi": cxx11_abi(),
    "cuda_available": torch.cuda.is_available(),
    "compiled_arch_list": torch.cuda.get_arch_list(),
    "devices": [],
}

devices: list[dict[str, object]] = []
if torch.cuda.is_available():
    for index in range(torch.cuda.device_count()):
        props = torch.cuda.get_device_properties(index)
        device_report: dict[str, object] = {
            "index": index,
            "name": props.name,
            "capability": list(torch.cuda.get_device_capability(index)),
            "total_memory_bytes": props.total_memory,
        }
        try:
            # This uses PyTorch's own CUDA kernels. Device enumeration alone does not.
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                value = (
                    torch.arange(
                        8, device=f"cuda:{index}", dtype=torch.float32
                    )
                    + 1
                ).sum()
                torch.cuda.synchronize(index)
            device_report["core_op"] = "pass"
            device_report["core_op_value"] = value.item()
            device_report["warnings"] = [str(item.message) for item in caught]
        except Exception as error:  # Preserve the exact CUDA error for diagnosis.
            device_report["core_op"] = "fail"
            device_report["error_type"] = type(error).__name__
            device_report["error"] = str(error)
        devices.append(device_report)

report["devices"] = devices
print(json.dumps(report, indent=2))
