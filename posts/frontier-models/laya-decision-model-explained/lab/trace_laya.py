#!/usr/bin/env python3
"""Trace one support ticket and three typed questions through Laya on a CPU.

Lab for "What a Decision Model Is, Traced Through Laya" (canery.in). Tier B:
CPU PyTorch, no GPU. It calls Laya's public predict() once, captures the
intermediate tensors of that same forward pass with hooks, recomputes the
returned probabilities from the captured logits, and checks they agree.

Run:   python trace_laya.py                 # English checkpoint, full trace
       python trace_laya.py --all           # also the other two checkpoints
Writes trace.json beside this file and prints a summary.
"""
import argparse
import json
import os
import pathlib

os.environ.setdefault("USE_TF", "0")  # the Laya card: a TensorFlow install can deadlock load()

import numpy as np
import torch
from huggingface_hub import snapshot_download

import laya
from laya.common import QTYPES, collate_items, temp_bucket

REPO = "convaiinnovations/laya"
REVISION = "55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851"  # repo state read on 2026-09-26
HERE = pathlib.Path(__file__).resolve().parent

# The series' shared decision example: one ticket, three typed questions.
STATE = {
    "subject": "Charged twice after upgrading, and the app keeps logging us out",
    "body": ("Hi, we upgraded to the Team plan on 3 March and our card was charged twice "
             "(2 x $49). Since the upgrade the desktop app logs everyone out every few "
             "minutes, so nobody on the team can work. Please refund the duplicate charge "
             "and fix the logouts today. We have a client demo tomorrow morning."),
}
QUESTIONS = {
    "route": {
        "type": "choice",
        "instructions": "Which support team should own this ticket?",
        "criteria": {
            "billing": "charges, invoices and refunds",
            "technical": "bugs, crashes, login and sync errors",
            "account": "plan changes, seats and permissions",
            "sales": "pricing questions and new contracts",
        },
    },
    "urgency": {
        "type": "score",
        "instructions": "How urgent is this ticket?",
        "criteria": ["no action needed", "within a week", "within two days", "today",
                     "immediately, work is blocked"],
    },
    "refund": {
        "type": "noul",
        "instructions": "Does the customer ask for a refund?",
    },
}
# What an LLM in JSON mode would have to write out for the same three answers.
JSON_ANSWER = '{"route": "billing", "urgency": 3, "refund": true}'


def segments(ids, markers, tok):
    """Label every position: cls, question, sep, marker, option, state, pad."""
    labels = ["pad"] * len(ids)
    labels[0] = "cls"
    first_sep = ids.index(tok.sep_token_id)
    for i in range(1, first_sep):
        labels[i] = "question"
    labels[first_sep] = "sep"
    opt_end = ids.index(tok.sep_token_id, markers[-1])  # the [SEP] after the last option
    for i in range(markers[0], opt_end):
        labels[i] = "option"
    for m in markers:
        labels[m] = "marker"
    labels[opt_end] = "sep"
    last = len(ids) - 1
    for i in range(opt_end + 1, last):
        labels[i] = "state"
    labels[last] = "sep"
    return labels


def count_params(model):
    """Parameters by component. Buffers (RoPE tables, the temperature vector) are excluded."""
    groups = {}
    for name, p in model.named_parameters():
        if name.startswith("encoder.embeddings"):
            g = "backbone: token embeddings + norm"
        elif name.startswith("encoder.layers"):
            part = name.split(".")[3]  # attn / mlp / attn_norm / mlp_norm
            g = {"attn": "backbone: attention", "mlp": "backbone: GeGLU MLP"}.get(part, "backbone: norms")
        elif name.startswith("encoder."):
            g = "backbone: norms"
        elif name.startswith("head."):
            g = "decision head: 2 transformer layers"
        elif name.startswith("type_emb"):
            g = "decision head: question-type embedding"
        elif name.startswith("scorer"):
            g = "decision head: option scorer"
        elif name.startswith("act_head"):
            g = "decision head: act/escalate head"
        else:
            g = "other: " + name
        groups[g] = groups.get(g, 0) + p.numel()
    return groups


def local_checkpoint(subfolder=None):
    """Download one checkpoint at the pinned commit (laya 0.3.20's load() cannot pin one)."""
    pre = subfolder + "/" if subfolder else ""
    root = snapshot_download(REPO, revision=REVISION, allow_patterns=[
        pre + "rl_agent_config.json", pre + "model.safetensors", pre + "encoder/*", pre + "tokenizer/*"])
    return os.path.join(root, subfolder) if subfolder else root


def trace(subfolder=None, full=True):
    agent = laya.load(local_checkpoint(subfolder), device="cpu")
    model, tok, cfg = agent.model, agent.tok, agent.cfg
    ids = list(QUESTIONS)
    internal = {q: agent._to_internal(QUESTIONS[q]) for q in ids}
    items = agent._encode_state(STATE, ids, internal)  # exactly what predict() builds
    batch = collate_items([items], tok.pad_token_id)

    # Forward hooks only record. A hook that returns a value replaces the module's output.
    seen = {}

    def keep_input_ids(module, args, kwargs):
        seen["input_ids"] = kwargs["input_ids"].clone()

    def keep_backbone(module, args, kwargs, out):
        seen["backbone"] = out.last_hidden_state.detach().clone()

    def keep_scorer(module, args, out):
        seen["marker_states"] = args[0].detach().clone()
        seen["scores"] = out.detach().clone()

    def keep(name):
        def hook(module, args, out):
            seen[name] = out.detach().clone()
        return hook

    hooks = [
        model.encoder.register_forward_pre_hook(keep_input_ids, with_kwargs=True),
        model.encoder.register_forward_hook(keep_backbone, with_kwargs=True),
        model.scorer.register_forward_hook(keep_scorer),
        model.head.layers[-1].register_forward_hook(keep("head_out")),
        model.act_head.register_forward_hook(keep("act_logits")),
    ]
    with torch.no_grad():
        api = agent.predict(STATE, QUESTIONS)
    for h in hooks:
        h.remove()

    # The batch predict() ran must be the batch we built.
    assert torch.equal(seen["input_ids"], batch["input_ids"]), "predict() built a different batch"

    out = {"checkpoint": subfolder or "english (repo root)", "revision": REVISION,
           "max_len": cfg["max_len"], "head_max_len": cfg["head_max_len"],
           "encoder": cfg["encoder"], "hidden_size": model.encoder.config.hidden_size,
           "vocab_size": model.encoder.config.vocab_size,
           "api_response": api, "params": count_params(model)}
    out["params_total"] = sum(out["params"].values())
    out["params_backbone"] = sum(v for k, v in out["params"].items() if k.startswith("backbone"))
    out["params_head"] = out["params_total"] - out["params_backbone"]

    logits = seen["scores"].squeeze(-1).float().numpy()  # [questions, max options], before masking
    questions = []
    for r, qid in enumerate(ids):
        it, q = items[r], internal[qid]
        k = len(it["markers"])
        qt = QTYPES[q["t"]]
        bucket = temp_bucket(qt, k)
        t_used = agent.temperature_by_options.get(bucket, agent.temperature[qt])
        z = logits[r, :k]
        p_raw = np.exp(z - z.max()); p_raw /= p_raw.sum()
        p_cal = np.exp(z / t_used - (z / t_used).max()); p_cal /= p_cal.sum()
        ans = api["answers"][qid]
        api_p = list(ans["probabilities"].values()) if "probabilities" in ans else [1 - ans["noul"], ans["noul"]]
        assert np.allclose(np.round(p_cal, 4), api_p, atol=1.5e-4), (qid, p_cal, api_p)
        row = {"id": qid, "type": q["t"], "n_options": k, "seq_len": len(it["ids"]),
               "markers": it["markers"], "logits": [round(float(v), 4) for v in z],
               "temperature_bucket": bucket, "temperature": round(float(t_used), 4),
               "p_raw": [round(float(v), 4) for v in p_raw], "p_returned": [round(float(v), 4) for v in p_cal],
               "act_probability": ans["action"]["act_probability"]}
        if full:
            row["tokens"] = tok.convert_ids_to_tokens(it["ids"])
            row["token_ids"] = it["ids"]
            row["segments"] = segments(it["ids"], it["markers"], tok)
            ends = it["markers"][1:] + [it["ids"].index(tok.sep_token_id, it["markers"][-1])]
            row["options_rendered"] = [tok.decode(it["ids"][m + 1:end]).strip()
                                       for m, end in zip(it["markers"], ends)]
        questions.append(row)
    out["questions"] = questions

    state_text = json.dumps(STATE, ensure_ascii=False)
    out["state_serialized"] = state_text
    out["state_tokens"] = len(tok(state_text, add_special_tokens=False)["input_ids"])
    out["shapes"] = {
        "input_ids": list(batch["input_ids"].shape),
        "attention_mask_rows": batch["attention_mask"].sum(1).tolist(),
        "backbone_out": list(seen["backbone"].shape),
        "head_out": list(seen["head_out"].shape),
        "marker_states": list(seen["marker_states"].shape),
        "scorer_out": list(seen["scores"].shape),
        "act_logits": list(seen["act_logits"].shape),
    }
    # Why act_probability reads 1.0: the pre-norm head layers leave the residual stream
    # unnormalised, and the act head reads the [CLS] vector without a LayerNorm (issue #185).
    out["scale"] = {
        "cls_norm_backbone": [round(float(v), 1) for v in seen["backbone"][:, 0].norm(dim=-1)],
        "cls_norm_after_head": [round(float(v), 1) for v in seen["head_out"][:, 0].norm(dim=-1)],
        "act_logits": [[round(float(v), 1) for v in row] for row in seen["act_logits"]],
    }
    out["usage"] = api["usage"]
    if full:
        out["json_answer"] = JSON_ANSWER
        out["json_answer_tokens_modernbert_bpe"] = len(tok(JSON_ANSWER, add_special_tokens=False)["input_ids"])
        out["special_tokens"] = {"cls": tok.cls_token, "sep": tok.sep_token, "mask": tok.mask_token,
                                 "mask_id": tok.mask_token_id, "pad_id": tok.pad_token_id}
    return out


def budget_sweep(max_k=140):
    """How build_sequence shares the question budget as the option count grows.

    Uses laya's own build_sequence on the route question with k synthetic options, each
    "optNN: <eight words>" (about the length of the ticket's route options), under the
    English budget (512 / 192) and the 1,024 / 256 budget of the other two checkpoints.
    """
    from transformers import AutoTokenizer
    from laya.common import build_sequence
    tok = AutoTokenizer.from_pretrained(os.path.join(local_checkpoint(), "tokenizer"))
    words = "charges invoices refunds bugs crashes seats contracts pricing".split()
    rows = []
    for max_len, head_max_len in ((512, 192), (1024, 256)):
        for k in range(1, max_k + 1):
            crit = {"opt%02d" % i: " ".join(words[(i + j) % 8] for j in range(8)) for i in range(k)}
            q = {"t": "choice", "ins": QUESTIONS["route"]["instructions"], "crit": crit}
            ids, markers = build_sequence(tok, STATE, q, max_len, head_max_len)
            sep = ids.index(tok.sep_token_id)
            # laya only checks that every marker survived; the [SEP] closing the options and
            # the whole state can still have been cut off by max_len.
            closed = tok.sep_token_id in ids[markers[-1]:] if markers else False
            if len(markers) == k and closed:
                opt_end = ids.index(tok.sep_token_id, markers[-1])
                per_option = (opt_end - markers[0]) / k  # tokens per option, marker included
                state_tokens = len(ids) - opt_end - 2
                state_room = max_len - opt_end - 2  # what a long state would get
            else:
                per_option, state_tokens, state_room = None, 0, 0
            rows.append({"max_len": max_len, "head_max_len": head_max_len, "k": k,
                         "all_markers_kept": len(markers) == k, "options_closed": closed,
                         "question_tokens": sep - 1, "tokens_per_option": per_option,
                         "state_tokens": state_tokens, "state_room": state_room})
    full = len(tok(" opt00: " + " ".join(words), add_special_tokens=False)["input_ids"]) + 1
    return {"option_tokens_unshrunk": full, "rows": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="also trace the multilingual and typed-decisions checkpoints")
    args = ap.parse_args()
    torch.manual_seed(0)
    torch.set_num_threads(max(1, os.cpu_count() // 2))

    result = {"laya": laya.__version__ if hasattr(laya, "__version__") else "0.3.20",
              "torch": torch.__version__, "english": trace()}
    result["budget"] = budget_sweep()
    if args.all:
        result["others"] = [trace("multilingual", full=False), trace("typed-decisions", full=False)]

    (HERE / "trace.json").write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    e = result["english"]
    print("batch", e["shapes"]["input_ids"], "| usage", e["usage"])
    for q in e["questions"]:
        print("%-8s len=%3d markers=%s logits=%s T=%.4f p=%s act=%.4f" % (
            q["id"], q["seq_len"], q["markers"], q["logits"], q["temperature"], q["p_returned"], q["act_probability"]))
    print("params: backbone %d + head %d = %d" % (e["params_backbone"], e["params_head"], e["params_total"]))
    for o in result.get("others", []):
        print(o["checkpoint"], o["params_total"], {q["id"]: q["p_returned"] for q in o["questions"]})


if __name__ == "__main__":
    main()
