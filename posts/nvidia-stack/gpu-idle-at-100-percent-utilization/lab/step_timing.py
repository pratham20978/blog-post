#!/usr/bin/env python3
"""Time a real training step on the host's clock and on the GPU's clock.

Hardware tier B: one NVIDIA GPU and a CUDA build of PyTorch. Nothing else.

    python3 step_timing.py                                 # print the tables
    python3 step_timing.py --out results.json              # also write the results file
    python3 step_timing.py --instance "rented, 1x L4" --out results.json

This is the article's worked example run for real: an MLP with 100 parameter
tensors, trained with a for-loop AdamW, logging loss.item() between backward and
the optimizer. Then the same step with the article's fixes:

    as-written   loss.item() mid-step; AdamW(foreach=False)
    fix-1        the loss stays on the GPU; no sync inside the measured steps
    fix-2        fix-1 with AdamW's foreach implementation
    graph        fix-2 captured as one CUDA graph and replayed

For every variant and phase it reports three numbers:

    host_ms    time.perf_counter() around the phase: when the Python line returned
    event_ms   CUDA events around the phase: when the stream reached each marker
    kernel_ms  the phase's kernels alone, queued behind a one-thread spin kernel so
               the GPU never waits for the host (the article's "kernels ran" column)

and the step time a loop reports when it is timed with no final synchronize.
The numbers will differ from the article's model on every GPU. That is the point.
"""

from __future__ import annotations

import argparse
import ctypes
import datetime
import json
import pathlib
import platform
import statistics
import time
import warnings

import torch
import torch.nn.functional as F
from torch import nn

DEVICE = "cuda"


# ------------------------------------------------------------------ the two clocks
class TwoClocks:
    """Marks phase boundaries on both clocks. Reads the events once, at the end."""

    def __init__(self):
        self.marks = []                                   # (name, host_seconds, event)

    def mark(self, name):
        ev = torch.cuda.Event(enable_timing=True)
        ev.record()                                       # enqueued; returns at once
        self.marks.append((name, time.perf_counter(), ev))

    def phases(self):
        """[(phase, host_ms, event_ms)] -- synchronizes once."""
        torch.cuda.synchronize()
        out = []
        for (a, ta, ea), (_, tb, eb) in zip(self.marks, self.marks[1:]):
            if a != "end":
                out.append((a, 1e3 * (tb - ta), ea.elapsed_time(eb)))
        return out


class NoClocks:
    """Stands in for TwoClocks when a loop must be timed with nothing extra enqueued."""

    def mark(self, name):
        pass


# ------------------------------------------------------------------ the workload
def build(width, depth, device):
    layers = []
    for _ in range(depth):
        layers += [nn.Linear(width, width), nn.ReLU()]
    return nn.Sequential(*layers).to(device)


def eager_step(model, opt, x, y, clocks, *, mid_step_sync, running):
    clocks.mark("forward")
    loss = F.mse_loss(model(x), y)
    clocks.mark("backward")
    loss.backward()
    clocks.mark("log")
    if mid_step_sync:
        loss.item()                          # the sync point the article is about
    else:
        running += loss.detach()             # stays on the GPU: no sync
    clocks.mark("optimizer")
    opt.step()
    opt.zero_grad(set_to_none=True)
    clocks.mark("end")


def capture_step(model, opt, static_x, static_y):
    """PyTorch's whole-network capture recipe: warm up on a side stream, then capture."""
    side = torch.cuda.Stream()
    side.wait_stream(torch.cuda.current_stream())
    with torch.cuda.stream(side):
        for _ in range(3):
            opt.zero_grad(set_to_none=True)
            F.mse_loss(model(static_x), static_y).backward()
            opt.step()
    torch.cuda.current_stream().wait_stream(side)
    graph = torch.cuda.CUDAGraph()
    opt.zero_grad(set_to_none=True)
    with torch.cuda.graph(graph):
        static_loss = F.mse_loss(model(static_x), static_y)
        static_loss.backward()
        opt.step()
    return graph, static_loss


def graph_step(graph, static_x, x, clocks):
    clocks.mark("copy-in")
    static_x.copy_(x)                        # new data into the captured input tensor
    clocks.mark("replay")
    graph.replay()
    clocks.mark("end")


# ------------------------------------------------------------------ kernels alone
def cycles_per_ms():
    a, b = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    a.record()
    torch.cuda._sleep(2_000_000)
    b.record()
    torch.cuda.synchronize()
    return 2_000_000 / a.elapsed_time(b)


def kernels_alone(fn, spin_cycles):
    """GPU time of fn's kernels with the host out of the way.

    A one-thread spin kernel goes first. While it spins, the host issues all of
    fn's launches, so when the GPU reaches the start event every kernel is
    already queued and runs back to back. fn must not synchronize.
    """
    torch.cuda.synchronize()
    a, b = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    torch.cuda._sleep(spin_cycles)
    a.record()
    t0 = time.perf_counter()
    result = fn()
    host_ms = 1e3 * (time.perf_counter() - t0)
    b.record()
    torch.cuda.synchronize()
    return result, a.elapsed_time(b), host_ms


def eager_kernel_ms(model, opt, x, y, spin_cycles, spin_ms, *, mid_step_sync, running):
    out = {}
    loss, out["forward"], h1 = kernels_alone(lambda: F.mse_loss(model(x), y), spin_cycles)
    _, out["backward"], h2 = kernels_alone(loss.backward, spin_cycles)
    if mid_step_sync:
        out["log"] = 0.0                     # loss.item() copies a value; no kernel runs
    else:
        _, out["log"], _ = kernels_alone(lambda: running.add_(loss.detach()), spin_cycles)

    def step():
        opt.step()
        opt.zero_grad(set_to_none=True)
    _, out["optimizer"], h3 = kernels_alone(step, spin_cycles)
    if max(h1, h2, h3) > 0.8 * spin_ms:
        warnings.warn("the spin kernel did not cover the host's issue time; "
                      "raise --spin-ms or kernel_ms will include host gaps")
    return out


# ------------------------------------------------------------------ one variant
def run_variant(name, model, opt, batches, target, args, spin_cycles):
    running = torch.zeros((), device=DEVICE)
    mid = name == "as-written"
    graph = static_x = None
    if name == "graph":
        static_x = batches[0].clone()
        graph, _ = capture_step(model, opt, static_x, target)

    def one(clocks, i):
        x = batches[i % len(batches)]
        if graph is not None:
            graph_step(graph, static_x, x, clocks)
        else:
            eager_step(model, opt, x, target, clocks, mid_step_sync=mid, running=running)

    for i in range(args.warmup):
        one(NoClocks(), i)
    torch.cuda.synchronize()

    # Both clocks over the measured steps, read once at the end.
    clocks = TwoClocks()
    for i in range(args.steps):
        one(clocks, i)
    per_phase = {}
    for phase, host_ms, event_ms in clocks.phases():
        per_phase.setdefault(phase, ([], []))
        per_phase[phase][0].append(host_ms)
        per_phase[phase][1].append(event_ms)

    # The kernels alone, phase by phase: the median of five separate passes. This is a
    # different measurement from the events, so a GPU-bound step can read a little over 100%.
    passes = []
    for _ in range(5):
        if graph is None:
            passes.append(eager_kernel_ms(model, opt, batches[0], target, spin_cycles,
                                          args.spin_ms, mid_step_sync=mid, running=running))
        else:
            _, copy_ms, _ = kernels_alone(lambda: static_x.copy_(batches[0]), spin_cycles)
            _, replay_ms, _ = kernels_alone(graph.replay, spin_cycles)
            passes.append({"copy-in": copy_ms, "replay": replay_ms})
    kernels = {k: statistics.median(p[k] for p in passes) for k in passes[0]}

    # A loop timed with no final synchronize, then the same loop synchronized.
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    for i in range(args.steps):
        one(NoClocks(), i)
    naive = time.perf_counter() - t0
    torch.cuda.synchronize()
    synced = time.perf_counter() - t0
    running.item()                           # the one deferred log read, outside every timing

    phases = {}
    for phase, (hosts, events) in per_phase.items():
        phases[phase] = {
            "host_ms": round(statistics.median(hosts), 4),
            "event_ms": round(statistics.median(events), 4),
            "kernel_ms": round(kernels.get(phase, 0.0), 4),
        }
    step_events = sum(p["event_ms"] for p in phases.values())
    busy = sum(p["kernel_ms"] for p in phases.values())
    return {
        "phases": phases,
        "step_ms_host": round(sum(p["host_ms"] for p in phases.values()), 4),
        "step_ms_events": round(step_events, 4),
        "gpu_busy_ms": round(busy, 4),
        "utilization_by_definition_pct": round(100 * busy / step_events, 1) if step_events else None,
        "naive_loop_ms_per_step": round(1e3 * naive / args.steps, 4),
        "synced_loop_ms_per_step": round(1e3 * synced / args.steps, 4),
    }


def sync_points(model, opt, x, y):
    """Run one as-written step with PyTorch's sync debugging on, and keep what it says."""
    running = torch.zeros((), device=DEVICE)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        torch.cuda.set_sync_debug_mode("warn")
        try:
            eager_step(model, opt, x, y, TwoClocks(), mid_step_sync=True, running=running)
        finally:
            torch.cuda.set_sync_debug_mode("default")
    messages = [str(w.message).splitlines()[0][:200] for w in caught]
    return {"count": len(messages), "messages": messages}


# ------------------------------------------------------------------ provenance
def nvml_versions():
    """KMD version string and CUDA UMD ceiling, read from NVML rather than parsed from a tool."""
    try:
        nvml = ctypes.CDLL("libnvidia-ml.so.1")
    except OSError:
        return None, None
    if nvml.nvmlInit_v2() != 0:
        return None, None
    buf = ctypes.create_string_buffer(96)
    umd = ctypes.c_int(0)
    kmd = buf.value.decode() if nvml.nvmlSystemGetDriverVersion(buf, 96) == 0 else None
    ceiling = umd.value if nvml.nvmlSystemGetCudaDriverVersion_v2(ctypes.byref(umd)) == 0 else None
    nvml.nvmlShutdown()
    return kmd, ceiling


def cpu_model():
    try:
        for line in pathlib.Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or None


def provenance(instance):
    props = torch.cuda.get_device_properties(0)
    major, minor = torch.cuda.get_device_capability(0)
    kmd, umd = nvml_versions()
    return {
        "captured_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "gpu_name": props.name,
        "compute_capability": f"sm_{major}{minor}",
        "sm_count": props.multi_processor_count,
        "kmd_version": kmd,
        "cuda_umd_version": umd,
        "torch_version": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "cpu_model": cpu_model(),
        "python_version": platform.python_version(),
        "instance": instance,
    }


def provenance_line(p):
    umd = f"{p['cuda_umd_version'] // 1000}.{p['cuda_umd_version'] % 1000 // 10}" if p["cuda_umd_version"] else "?"
    return (f"Captured {p['captured_at_utc']} on {p['gpu_name']} ({p['compute_capability']}, "
            f"{p['sm_count']} SMs), KMD {p['kmd_version'] or '?'}, CUDA UMD {umd}, torch "
            f"{p['torch_version']} (runtime {p['torch_cuda_runtime']}), {p['cpu_model']}, "
            f"Python {p['python_version']}" + (f", {p['instance']}" if p["instance"] else "") + ".")


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--width", type=int, default=256)
    ap.add_argument("--depth", type=int, default=50, help="Linear layers; 2 parameter tensors each")
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--warmup", type=int, default=10)
    ap.add_argument("--steps", type=int, default=20)
    ap.add_argument("--spin-ms", type=float, default=200.0,
                    help="how long the spin kernel holds the GPU while a phase is issued")
    ap.add_argument("--instance", default=None, help="free text for the provenance line")
    ap.add_argument("--out", type=pathlib.Path, default=None, help="merge results into this JSON file")
    args = ap.parse_args()

    if not torch.cuda.is_available():
        raise SystemExit("step_timing.py is tier B: it needs an NVIDIA GPU and a CUDA build of "
                         "PyTorch. queue_model.py runs the same example with no GPU.")

    torch.manual_seed(0)
    spin_cycles = int(cycles_per_ms() * args.spin_ms)
    batches = [torch.randn(args.batch, args.width, device=DEVICE) for _ in range(4)]
    target = torch.randn(args.batch, args.width, device=DEVICE)

    results = {"provenance": provenance(args.instance), "step_timing": {
        "config": {"width": args.width, "depth": args.depth, "parameter_tensors": 2 * args.depth,
                   "batch": args.batch, "warmup_steps": args.warmup, "measured_steps": args.steps},
        "variants": {}}}

    variants = [("as-written", False, False), ("fix-1", False, False),
                ("fix-2", True, False), ("graph", True, True)]
    for name, foreach, capturable in variants:
        torch.manual_seed(0)
        model = build(args.width, args.depth, DEVICE)
        opt = torch.optim.AdamW(model.parameters(), lr=1e-4, foreach=foreach,
                                capturable=capturable)
        if name == "as-written":
            results["step_timing"]["sync_points"] = sync_points(model, opt, batches[0], target)
        results["step_timing"]["variants"][name] = run_variant(
            name, model, opt, batches, target, args, spin_cycles)

    print(provenance_line(results["provenance"]))
    sp = results["step_timing"]["sync_points"]
    print(f"\nsync points in one as-written step (set_sync_debug_mode): {sp['count']}")
    for m in sp["messages"]:
        print(f"   {m}")
    for name, v in results["step_timing"]["variants"].items():
        print(f"\n== {name}")
        print(f"   {'phase':<12}{'host timer':>12}{'CUDA events':>13}{'kernels alone':>15}")
        for phase, p in v["phases"].items():
            print(f"   {phase:<12}{p['host_ms']:>9.3f} ms{p['event_ms']:>10.3f} ms{p['kernel_ms']:>12.3f} ms")
        print(f"   step: host {v['step_ms_host']:.3f} ms, events {v['step_ms_events']:.3f} ms, "
              f"kernels {v['gpu_busy_ms']:.3f} ms, utilization by definition "
              f"{v['utilization_by_definition_pct']}%")
        print(f"   loop of {args.steps}: {v['naive_loop_ms_per_step']:.3f} ms/step without a final "
              f"sync, {v['synced_loop_ms_per_step']:.3f} ms/step with one")

    if args.out:
        merged = json.loads(args.out.read_text()) if args.out.exists() else {}
        merged.update(results)
        args.out.write_text(json.dumps(merged, indent=2) + "\n")
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
