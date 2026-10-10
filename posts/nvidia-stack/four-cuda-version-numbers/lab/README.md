# Lab — The Four CUDA Version Numbers

**Hardware tier: A — no GPU required.** Everything here was written and captured on an x86-64
Linux laptop with no NVIDIA GPU, no NVIDIA driver and no CUDA Toolkit installed. That is not a
compromise; it is the demonstration. Two of the four version numbers belong to artifacts you can
read before you install anything, and one of the two host numbers can be asked for even when the
hardware it describes is absent.

## Prerequisites

- `python3` (3.9 or newer — captured on 3.14.4). Standard library only; nothing to `pip install`.
- A network connection, for `cuda_versions.py` only. `check_host.py` needs nothing.
- Roughly 2 MB of transfer. The scripts read wheels over HTTP Range requests rather than
  downloading them, so a 554 MB `torch` wheel costs about 1.2 MB to inspect.

## Run order

```bash
python3 cuda_versions.py torch 2.14.0     # numbers 3 and 4, from the artifacts
python3 check_host.py                     # numbers 1 and 2, from this machine
```

Pass no arguments to `cuda_versions.py` and it reads whatever `torch` release is current, which
will not match the transcript below. Pin the release to reproduce it.

## What each script does

**`cuda_versions.py`** follows one framework's declared dependency chain down to the CUDA runtime
it will actually load, then reads the version out of that artifact three different ways:

1. `torch/version.py`, for the build-time CUDA the framework recorded about itself;
2. the pin chain — `torch` → `cuda-toolkit` → `nvidia-cuda-runtime` — for which runtime build
   `pip` would resolve;
3. `CUDART_VERSION` and `CUDA_VERSION`, read from the C headers inside that exact wheel;
4. finally, it extracts `libcudart.so.13` to a temporary directory, loads it with `ctypes`, and
   calls `cudaRuntimeGetVersion` for real.

Step 4 is the one worth watching. NVIDIA documents that since CUDA 12.0 the call returns a
compile-time constant and no longer initialises CUDA. If that is true, it must answer on a machine
with no driver — and it does.

**`check_host.py`** reads the two numbers that belong to the machine, each from the artifact that
owns it rather than from another tool's report of it:

- the kernel-mode driver, from `/proc/driver/nvidia/version`, which `nvidia.ko` writes;
- the CUDA driver ceiling, by loading `libcuda.so.1` and calling `cuDriverGetVersion`.

It deliberately does not parse `nvidia-smi` output. `nvidia-smi` is another reader of the same
driver, not the source of any of these numbers.

## Expected result

`expected-output.txt` holds both transcripts as captured. The parts that matter:

- `torch` 2.14.0 declares `cuda-toolkit[...]==13.0.3`, which pins `nvidia-cuda-runtime==13.0.96.*`,
  whose headers define `CUDART_VERSION` as `13000` — CUDA 13.0, matching the `cuda = '13.0'` that
  `torch/version.py` records.
- `torch/version.py` says `__version__ = '2.14.0+cu130'` while PyPI published the same
  distribution as `2.14.0`. The `+cu130` is a local version label and carries no meaning to any
  resolver.
- Loading the extracted `libcudart.so.13` and calling `cudaRuntimeGetVersion` returns `13000` on a
  machine with no GPU.
- `check_host.py` reports all four host-side lookups as absent, and says so per number rather than
  crashing. On a machine with a driver, numbers 1 and 2 fill in and the final comparison runs.

## On a machine that does have a GPU

`check_host.py` is the half of this lab that changes. It will print the loaded kernel module's
version, the driver's CUDA ceiling from `libcuda.so.1`, the runtime version of whichever
`libcudart` your environment would load, and `nvcc`'s release if a Toolkit is on `PATH` — then
compare the runtime against the ceiling and say whether a launch would work.

No GPU output is reproduced in this lab, because none was measured. The article states the same
rule and shows NVIDIA's own published transcripts for the cases that need real hardware.

## Cleanup

`cuda_versions.py` leaves one extracted `libcudart.so.13` under your system temporary directory;
the path is printed. Remove that directory when you are done. Nothing else is written, no package
is installed, and no environment variable is changed.
