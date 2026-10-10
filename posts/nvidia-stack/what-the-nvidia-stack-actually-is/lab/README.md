# Lab — What the NVIDIA Stack Actually Is

Companion to *What the NVIDIA Stack Actually Is*, part 1 of the NVIDIA Stack series.

**Hardware tier: A — no GPU required.** Nothing here needs an NVIDIA GPU, an NVIDIA
driver, or the CUDA Toolkit. That is the point: the whole stack can be read before any
of it is installed, on a laptop with integrated graphics. Every number printed in the
article was produced on exactly such a machine.

## Prerequisites

- Python 3.9 or newer. Standard library only — nothing to `pip install`.
- Outbound HTTPS to `pypi.org` and `files.pythonhosted.org`.
- About 60 MB of transfer for the first script, and roughly 700 MB for the second,
  which reads the ELF headers of every library in the dependency graph. Neither
  writes anything to disk.

## Run order

```bash
# 1. What is inside one wheel, and what will the loader be asked for?
python3 inspect_wheel.py torch 2.14.0

# 2. Who is supposed to provide each of those libraries?
python3 resolve_stack.py torch 2.14.0
```

Both take a package name and an optional version, so you can point them at anything:

```bash
python3 inspect_wheel.py nvidia-cublas
python3 resolve_stack.py torch          # whatever is current today
```

## Files

| File | What it does |
|---|---|
| `wheelio.py` | shared helpers: PyPI metadata, a seekable HTTP Range file, a minimal ELF64 dynamic-section reader. Imported by both scripts; not run directly. |
| `inspect_wheel.py` | lists a wheel's contents, reads its real `METADATA`, and prints `SONAME`, `DT_NEEDED` and `DT_RPATH` for each library it ships |
| `resolve_stack.py` | walks the declared dependency graph and maps every requested library to the wheel that provides it — or to the host driver |
| `expected-output.txt` | both runs captured on 2026-09-23, to diff against |

## What you should see

`inspect_wheel.py` lists all 13,043 entries of a 554.6 MB wheel after transferring
about 1.2 MB, because a zip's central directory sits at the end of the file and
`zipfile` will seek to it if the file object supports seeking.

`resolve_stack.py` ends on a single unresolved library:

```
libcuda.so.1               *** THE HOST NVIDIA DRIVER ***     libcaffe2_nvrtc.so
```

Everything else — cuBLAS, cuDNN, NCCL, cuSOLVER, the CUDA runtime — is delivered by a
Python wheel. `libcuda.so.1` is not, and cannot be. That one line is the article.

## Caveats

- Package versions move. The output you get will not match `expected-output.txt`
  exactly, and the differences are worth reading: they are this stack's release
  churn, visible in a diff.
- The two largest libraries in the PyTorch wheel are skipped. Their ELF dynamic
  section sits hundreds of megabytes into the file, and reading it would mean
  streaming most of the library. Both scripts say so rather than quietly omitting them.
- The dependency-marker evaluator in `resolve_stack.py` handles the subset of PEP 508
  these packages use, assuming Linux x86_64 and CPython. Unrecognised markers are
  allowed through rather than dropped, so the graph errs toward showing too much.
- Read-only. Nothing is installed, nothing is cached, nothing is written.
