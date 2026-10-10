# Lab — What a Decision Model Is, Traced Through Laya

One script that sends a support ticket and three typed questions through Laya on a CPU. It prints
and saves every number the article uses. This is a **Tier B** lab: it needs PyTorch, which runs on
a CPU here, with no GPU.

The script does not reimplement Laya. It calls the library's own `predict()` once and records what
each module produced during that call, using PyTorch forward hooks. It then recomputes the returned
probabilities from the captured logits, and stops with an error if they disagree.

## Files

| File | What it is |
|---|---|
| `README.md` | this file |
| `requirements.txt` | the pinned environment |
| `trace_laya.py` | the trace, the parameter count and the option-budget sweep |
| `trace.json` | the output captured for the article, for comparison with your run |

## Prerequisites

| | |
|---|---|
| Hardware | any x86-64 or Apple Silicon machine with 4 GB of free RAM; no GPU needed |
| Python | 3.12 (the environment was built and run with 3.12.13) |
| Disk | about 1 GB for the Python packages, plus 842 MB of weights for the English checkpoint; `--all` adds 644 MB and 842 MB for the other two |
| Network | the first run downloads the weights from Hugging Face; later runs use the local cache |
| Time | a minute or two after the download |

## Run order

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python --index-strategy unsafe-best-match -r requirements.txt
.venv/bin/python trace_laya.py            # the English checkpoint: the article's worked example
.venv/bin/python trace_laya.py --all      # also laya-multilingual and laya-typed-decisions
```

With plain `pip`, run `python -m venv .venv` and then `.venv/bin/pip install -r requirements.txt`.

`requirements.txt` pulls the **CPU build** of PyTorch from PyTorch's own index on Linux and Windows.
Without that index, a Linux install resolves the CUDA build instead: about 4.5 GB more, and the same
numbers on a CPU.

The weights are pinned to Hugging Face commit `55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851` of
`convaiinnovations/laya`, which holds all three checkpoints. laya 0.3.20's `load()` cannot pin a
commit, so the script downloads that commit with `huggingface_hub` and loads it from the local
path.

## What to expect

The script prints the batch shape and token usage, one line per question, and the parameter count:

```text
batch [3, 141] | usage {'input_tokens': 399, 'output_tokens': 0}
route    len=141 markers=[13, 23, 34, 43] logits=[4.1957, -0.0121, -1.0685, -1.5121] T=1.7602 p=[0.8468, 0.0776, 0.0426, 0.0331] act=1.0000
urgency  len=136 markers=[11, 18, 25, 32, 37] logits=[-2.715, -0.3012, 1.5369, 2.6428, 3.3203] T=1.2514 p=[0.0043, 0.0294, 0.1275, 0.3086, 0.5303] act=1.0000
refund   len=122 markers=[14, 24] logits=[-2.3921, 1.1858] T=1.9834 p=[0.1414, 0.8586] act=1.0000
params: backbone 394781696 + head 26512131 = 421293827
```

With `--all` it adds one line for each of the other two checkpoints:

```text
multilingual 321908995 {'route': [1.0, 0.0, 0.0, 0.0], 'urgency': [0.0048, 0.0957, 0.0902, 0.708, 0.1013], 'refund': [0.0244, 0.9756]}
typed-decisions 421293827 {'route': [0.4576, 0.2782, 0.1488, 0.1154], 'urgency': [0.0049, 0.0415, 0.0938, 0.463, 0.3967], 'refund': [0.3208, 0.6792]}
```

It writes `trace.json` beside itself, overwriting the copy shipped here. Keep the shipped copy
somewhere else first if you want to compare the two.

Probabilities should match to four decimals, since the model runs in FP32 on the CPU. Logits can
differ in the fifth decimal between CPUs, because matrix multiplication adds numbers in a different
order on different hardware.

Two warnings are normal. laya prints a `RuntimeWarning` that the checkpoint's `choice:11+`
temperature (0.1006) is outside 0.5–5 and has been clamped; it does not affect this ticket's
questions. transformers prints a note about `clean_up_tokenization_spaces`, which changes nothing
here.

### What `trace.json` holds

- `english`: the rendered options, every token and its segment, the marker positions, the tensor
  shapes, the logits, the applied temperature, the probabilities at T = 1 and as returned, the full
  API response, the parameter count per component, and the `[CLS]` norms and act logits that show
  why `act_probability` is 1.0.
- `budget`: for 1 to 140 options under the 512 / 192 and 1,024 / 256 budgets, the tokens each option
  keeps, the question's tokens, and the room left for the state. Computed with laya's own
  `build_sequence`.
- `others`: the same trace, without the per-token detail, for `laya-multilingual` and
  `laya-typed-decisions`.

## Safety and cleanup

The script reads a fixed, made-up ticket and talks to no service except Hugging Face, for the
download. It never contacts TypeSafe's API.

To remove everything:

```bash
rm -rf .venv
rm -rf ~/.cache/huggingface/hub/models--convaiinnovations--laya
```
