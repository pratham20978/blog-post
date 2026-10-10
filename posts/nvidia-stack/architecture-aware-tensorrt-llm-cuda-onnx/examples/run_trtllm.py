#!/usr/bin/env python3
"""Minimal TensorRT-LLM 1.2 PyTorch-backend generation."""

from __future__ import annotations

import argparse

from tensorrt_llm import LLM, SamplingParams


parser = argparse.ArgumentParser()
parser.add_argument(
    "--model",
    default="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    help="Supported Hugging Face identifier or local checkpoint",
)
parser.add_argument("--max-tokens", type=int, default=64)
args = parser.parse_args()

llm = LLM(model=args.model)
sampling = SamplingParams(
    max_tokens=args.max_tokens,
    temperature=0.8,
    top_p=0.95,
)

for result in llm.generate(
    ["CUDA compute capability is", "A reproducible benchmark records"],
    sampling,
):
    print(f"prompt={result.prompt!r}")
    print(f"completion={result.outputs[0].text!r}")
