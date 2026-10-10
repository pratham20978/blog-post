#!/usr/bin/env python3
"""Read nvidia-smi's utilization number while the GPU does four very different things.

Hardware tier B: one NVIDIA GPU, its driver (for libnvidia-ml.so.1) and a CUDA
build of PyTorch.

    python3 util_probe.py                          # about 25 seconds
    python3 util_probe.py --seconds 10 --out results.json

The number is read from NVML -- nvmlDeviceGetUtilizationRates, the call
nvidia-smi and most monitoring agents are built on -- every 100 ms, in four
phases of the same length:

    idle             nothing queued
    spin_one_thread  torch.cuda._sleep: one block of one thread, spinning
    full_width       back-to-back large matmuls
    tiny_launches    a Python loop of one-element additions, as fast as the host goes

NVIDIA documents the number as the share of the sample window in which some
kernel was executing. By that definition spin_one_thread reads ~100%, and
tiny_launches reads roughly the share of time a tiny kernel is actually running,
which this script estimates independently. The article cites one study that saw
the counter read 100% on a GPU executing kernels a few percent of the time. This
script finds out which description fits your GPU.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import pathlib
import statistics
import threading
import time

import torch

SAMPLE_S = 0.100
SETTLE_S = 1.0          # the counter averages over up to 1 s: drop each phase's first second


class Utilization(ctypes.Structure):
    _fields_ = [("gpu", ctypes.c_uint), ("memory", ctypes.c_uint)]


class NVML:
    def __init__(self, index=0):
        self.lib = ctypes.CDLL("libnvidia-ml.so.1")
        if self.lib.nvmlInit_v2() != 0:
            raise SystemExit("nvmlInit failed: is the NVIDIA driver loaded?")
        self.handle = ctypes.c_void_p()
        if self.lib.nvmlDeviceGetHandleByIndex_v2(index, ctypes.byref(self.handle)) != 0:
            raise SystemExit(f"no NVML device at index {index}")

    def gpu_util(self):
        u = Utilization()
        if self.lib.nvmlDeviceGetUtilizationRates(self.handle, ctypes.byref(u)) != 0:
            return None                      # e.g. MIG-enabled GPUs do not support the query
        return u.gpu

    def close(self):
        self.lib.nvmlShutdown()


class Sampler(threading.Thread):
    """Polls NVML in the background and tags each sample with the current phase."""

    def __init__(self, nvml):
        super().__init__(daemon=True)
        self.nvml, self.phase, self.samples, self.stop = nvml, None, [], threading.Event()

    def run(self):
        while not self.stop.is_set():
            value = self.nvml.gpu_util()
            if self.phase and value is not None:
                self.samples.append((self.phase, time.monotonic(), value))
            time.sleep(SAMPLE_S)


def keep_queue_busy(launch, seconds):
    """Launch back to back, never letting the stream run dry and never queueing unboundedly."""
    in_flight = []
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        launch()
        ev = torch.cuda.Event()
        ev.record()
        in_flight.append(ev)
        if len(in_flight) > 2:
            in_flight.pop(0).synchronize()   # wait for the oldest; two stay queued
    torch.cuda.synchronize()


def tiny_launches(seconds):
    x = torch.zeros(1, device="cuda")
    n, deadline = 0, time.monotonic() + seconds
    while time.monotonic() < deadline:
        for _ in range(1000):
            x.add_(1)
        n += 1000
        torch.cuda.synchronize()             # once per 1,000 launches: keeps the queue bounded
    return n / seconds


def tiny_kernel_ms(spin_50ms, n=2000):
    """GPU time of one tiny add, measured with the launches queued behind a spin kernel.

    The spin (~300 ms) must outlast the host's time to queue n adds, or the
    measurement would include the gaps between launches it is trying to exclude.
    """
    x = torch.zeros(1, device="cuda")
    a, b = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    torch.cuda.synchronize()
    torch.cuda._sleep(6 * spin_50ms)
    a.record()
    t0 = time.monotonic()
    for _ in range(n):
        x.add_(1)
    issue_s = time.monotonic() - t0
    b.record()
    torch.cuda.synchronize()
    if issue_s > 0.25:
        print(f"   warning: queuing {n} adds took {issue_s * 1000:.0f} ms, longer than the spin")
    return a.elapsed_time(b) / n


def summarize(samples, phase, t0):
    vals = [v for p, t, v in samples if p == phase and t - t0[phase] >= SETTLE_S]
    if not vals:
        return {"nvml_gpu_util_pct_mean": None, "nvml_gpu_util_pct_min": None,
                "nvml_gpu_util_pct_max": None, "samples": 0}
    return {"nvml_gpu_util_pct_mean": round(statistics.mean(vals), 1),
            "nvml_gpu_util_pct_min": min(vals), "nvml_gpu_util_pct_max": max(vals),
            "samples": len(vals)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seconds", type=float, default=6.0, help="length of each phase")
    ap.add_argument("--size", type=int, default=8192, help="matrix side for full_width")
    ap.add_argument("--out", type=pathlib.Path, default=None, help="merge results into this JSON file")
    args = ap.parse_args()

    if not torch.cuda.is_available():
        raise SystemExit("util_probe.py is tier B: it needs an NVIDIA GPU and a CUDA build of PyTorch.")

    nvml = NVML()
    sampler = Sampler(nvml)
    sampler.start()
    t0 = {}

    def phase(name):
        torch.cuda.synchronize()
        t0[name] = time.monotonic()
        sampler.phase = name

    # cycles for ~50 ms of spinning, so one _sleep call is far longer than one launch
    a, b = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    a.record()
    torch.cuda._sleep(1_000_000)
    b.record()
    torch.cuda.synchronize()
    spin = int(1_000_000 / a.elapsed_time(b) * 50)
    m = torch.randn(args.size, args.size, device="cuda")

    phase("idle")
    time.sleep(args.seconds)
    phase("spin_one_thread")
    keep_queue_busy(lambda: torch.cuda._sleep(spin), args.seconds)
    phase("full_width")
    keep_queue_busy(lambda: m @ m, args.seconds)
    phase("tiny_launches")
    rate = tiny_launches(args.seconds)
    sampler.phase = None
    per_kernel = tiny_kernel_ms(spin)

    sampler.stop.set()
    sampler.join()
    nvml.close()

    phases = {name: summarize(sampler.samples, name, t0) for name in t0}
    phases["tiny_launches"]["launches_per_second"] = round(rate)
    phases["tiny_launches"]["estimated_kernel_busy_pct"] = round(100 * rate * per_kernel / 1000, 1)

    print(f"{torch.cuda.get_device_name(0)}: NVML GPU utilization, sampled every "
          f"{int(SAMPLE_S * 1000)} ms, first {SETTLE_S:.0f} s of each phase dropped\n")
    print(f"   {'phase':<18}{'mean':>7}{'min':>6}{'max':>6}{'samples':>9}")
    for name, s in phases.items():
        if s["samples"]:
            print(f"   {name:<18}{s['nvml_gpu_util_pct_mean']:>6}%{s['nvml_gpu_util_pct_min']:>5}%"
                  f"{s['nvml_gpu_util_pct_max']:>5}%{s['samples']:>9}")
        else:
            print(f"   {name:<18}   no samples (is utilization supported on this GPU?)")
    t = phases["tiny_launches"]
    print(f"\n   tiny_launches: {t['launches_per_second']:,} launches/s x {per_kernel * 1000:.2f} us "
          f"per kernel = GPU executing kernels ~{t['estimated_kernel_busy_pct']}% of the time")

    if args.out:
        merged = json.loads(args.out.read_text()) if args.out.exists() else {}
        merged["util_probe"] = {"sample_interval_ms": SAMPLE_S * 1000, "phases": phases}
        args.out.write_text(json.dumps(merged, indent=2) + "\n")
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
