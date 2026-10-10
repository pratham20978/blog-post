#!/usr/bin/env python3
"""Export a small dynamic-shape PyTorch graph through the dynamo ONNX path."""

from __future__ import annotations

import argparse
from pathlib import Path

import onnx
import torch
from torch import nn


class TokenProjector(nn.Module):
    def __init__(self, vocab_size: int = 256, hidden_size: int = 64) -> None:
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        self.projection = nn.Linear(hidden_size, vocab_size, bias=False)

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        return self.projection(self.embedding(input_ids))


parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path, default=Path("token_projector.onnx"))
args = parser.parse_args()

model = TokenProjector().eval()
example = torch.randint(0, 256, (2, 16), dtype=torch.int64)
batch = torch.export.Dim("batch", min=1, max=8)
sequence = torch.export.Dim("sequence", min=1, max=2048)

torch.onnx.export(
    model,
    (example,),
    args.output,
    input_names=["input_ids"],
    output_names=["logits"],
    dynamo=True,
    dynamic_shapes=({0: batch, 1: sequence},),
)

graph = onnx.load(args.output)
onnx.checker.check_model(graph)
inferred = onnx.shape_inference.infer_shapes(graph)
onnx.save(inferred, args.output)
print(f"validated {args.output}")
