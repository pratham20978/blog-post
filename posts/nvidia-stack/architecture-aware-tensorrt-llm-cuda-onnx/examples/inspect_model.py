#!/usr/bin/env python3
"""Resolve a Hugging Face model class without loading model weights."""

from __future__ import annotations

import argparse
import json

from transformers import AutoConfig


parser = argparse.ArgumentParser()
parser.add_argument("model")
parser.add_argument("--revision", required=True, help="Commit, tag, or branch to audit")
args = parser.parse_args()

config = AutoConfig.from_pretrained(
    args.model,
    revision=args.revision,
    trust_remote_code=False,
)

print(
    json.dumps(
        {
            "repository": args.model,
            "requested_revision": args.revision,
            "resolved_commit": getattr(config, "_commit_hash", None),
            "model_type": getattr(config, "model_type", None),
            "architectures": getattr(config, "architectures", None),
            "hidden_size": getattr(config, "hidden_size", None),
            "layers": getattr(config, "num_hidden_layers", None),
            "attention_heads": getattr(config, "num_attention_heads", None),
            "kv_heads": getattr(config, "num_key_value_heads", None),
            "max_positions": getattr(config, "max_position_embeddings", None),
            "dtype": str(getattr(config, "torch_dtype", None)),
        },
        indent=2,
    )
)
