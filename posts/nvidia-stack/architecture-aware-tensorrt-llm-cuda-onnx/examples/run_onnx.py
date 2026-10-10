#!/usr/bin/env python3
"""Run the ONNX probe with TensorRT→CUDA→CPU provider fallback."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import onnxruntime as ort


parser = argparse.ArgumentParser()
parser.add_argument("model", type=Path)
parser.add_argument("--batch", type=int, default=2)
parser.add_argument("--sequence", type=int, default=16)
parser.add_argument("--engine-cache", type=Path, default=Path(".ort_trt_cache"))
args = parser.parse_args()

available = set(ort.get_available_providers())
providers: list[str | tuple[str, dict[str, object]]] = []

if "TensorrtExecutionProvider" in available:
    args.engine_cache.mkdir(parents=True, exist_ok=True)
    providers.append(
        (
            "TensorrtExecutionProvider",
            {
                "trt_engine_cache_enable": True,
                "trt_engine_cache_path": str(args.engine_cache),
            },
        )
    )
if "CUDAExecutionProvider" in available:
    providers.append("CUDAExecutionProvider")
providers.append("CPUExecutionProvider")

session = ort.InferenceSession(str(args.model), providers=providers)
input_ids = np.random.default_rng(0).integers(
    0,
    256,
    size=(args.batch, args.sequence),
    dtype=np.int64,
)
outputs = session.run(None, {"input_ids": input_ids})

print(
    json.dumps(
        {
            "available_providers": sorted(available),
            "session_providers": session.get_providers(),
            "input_shape": list(input_ids.shape),
            "output_shapes": [list(value.shape) for value in outputs],
        },
        indent=2,
    )
)
