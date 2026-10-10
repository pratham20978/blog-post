#!/usr/bin/env python3
"""A deterministic model of one CUDA stream: the host issues work, the GPU runs it in order.

Hardware tier A -- no GPU, no CUDA, no third-party packages. It reproduces every
number in the article's worked example, so the arithmetic can be checked without
renting anything:

    python3 queue_model.py                 # the step, its fixes and the exercises, as tables
    python3 queue_model.py --trace         # also print the queue depth over one step
    python3 queue_model.py --json          # machine-readable, for plotting

The durations are model inputs chosen to be followed by hand. They are NOT
measurements. step_timing.py measures the real ones on a GPU (tier B).

The model has three rules, and they are the whole of CUDA's single-stream
behaviour that the article relies on:

1. The host pays `host_us` to issue each kernel. The kernel joins the queue when
   that cost has been paid.
2. The GPU starts a kernel when it has arrived AND the previous kernel in the
   same stream has finished:  start = max(arrival, previous_end).
3. A synchronisation point stops the host clock until the GPU has finished
   everything issued so far:  host = max(host, gpu_free).

An event recorded between two phases is time-stamped when the GPU reaches it,
which is max(host_time_recorded, gpu_free). A host timer read at the same line
reads the host clock. The difference between those two clocks is the article.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Phase:
    name: str
    kernels: int = 0          # how many kernels this phase issues
    host_us: float = 0.0      # host cost to issue ONE kernel (Python + dispatch + launch)
    gpu_us: float = 0.0       # GPU execution time of ONE kernel
    sync: bool = False        # True: this line blocks the host until the GPU drains


@dataclass
class StepResult:
    naive_ms: dict = field(default_factory=dict)     # host clock, per phase
    event_ms: dict = field(default_factory=dict)     # GPU clock, per phase
    kernel_ms: dict = field(default_factory=dict)    # GPU busy inside each phase
    spans: dict = field(default_factory=dict)        # phase -> (host0, host1, gpu0, gpu1), ms
    wall_ms: float = 0.0
    busy_ms: float = 0.0
    depth: list = field(default_factory=list)        # (time_ms, kernels waiting or running)
    kernels: list = field(default_factory=list)      # (start_ms, end_ms) of every kernel


def run(phases, steps=1):
    """Simulate `steps` back-to-back iterations of `phases` on one stream."""
    host = 0.0          # host clock, microseconds
    gpu_free = 0.0      # when the GPU finishes everything issued so far
    busy = 0.0
    results = []
    in_flight = []      # (arrival, end) of every kernel, for the queue-depth trace

    for _ in range(steps):
        r = StepResult()
        step_host0 = host
        step_event0 = max(host, gpu_free)
        for ph in phases:
            h0 = host
            e0 = max(host, gpu_free)          # event recorded before this phase
            kbusy = 0.0
            first_start = None
            if ph.sync:
                host = max(host, gpu_free)    # rule 3
            for _ in range(ph.kernels):
                host += ph.host_us            # rule 1
                start = max(host, gpu_free)   # rule 2
                first_start = start if first_start is None else first_start
                gpu_free = start + ph.gpu_us
                busy += ph.gpu_us
                kbusy += ph.gpu_us
                in_flight.append((host, gpu_free))
                r.kernels.append((start / 1000, gpu_free / 1000))
            e1 = max(host, gpu_free)          # event recorded after this phase
            r.naive_ms[ph.name] = (host - h0) / 1000
            r.event_ms[ph.name] = (e1 - e0) / 1000
            r.kernel_ms[ph.name] = kbusy / 1000
            r.spans[ph.name] = (h0 / 1000, host / 1000,
                                (first_start if first_start is not None else e0) / 1000,
                                gpu_free / 1000 if ph.kernels else e0 / 1000)
        r.wall_ms = (max(host, gpu_free) - step_host0) / 1000
        r.busy_ms = sum(r.kernel_ms.values())
        r.event_total_ms = (max(host, gpu_free) - step_event0) / 1000
        r.host_end_ms = host / 1000
        r.gpu_end_ms = gpu_free / 1000
        results.append(r)

    # Queue depth: kernels issued but not yet finished, sampled at every change.
    edges = sorted([(a, +1) for a, _ in in_flight] + [(e, -1) for _, e in in_flight])
    depth, trace = 0, []
    for t, d in edges:
        depth += d
        trace.append((round(t / 1000, 4), depth))
    return results, trace, host / 1000, gpu_free / 1000, busy / 1000


# ------------------------------------------------------------------ the worked example
PER_LAUNCH_US = 20.0   # host cost per kernel: a model input, see the article

AS_WRITTEN = [
    Phase("forward", kernels=40, host_us=PER_LAUNCH_US, gpu_us=100.0),
    Phase("backward", kernels=80, host_us=PER_LAUNCH_US, gpu_us=100.0),
    Phase("loss.item()", sync=True),
    Phase("optimizer", kernels=1000, host_us=PER_LAUNCH_US, gpu_us=3.0),
]

NO_MID_STEP_SYNC = [p for p in AS_WRITTEN if not p.sync]

FEWER_LAUNCHES = [
    Phase("forward", kernels=40, host_us=PER_LAUNCH_US, gpu_us=100.0),
    Phase("backward", kernels=80, host_us=PER_LAUNCH_US, gpu_us=100.0),
    # the same 3.0 ms of optimizer arithmetic, issued as 10 larger kernels
    Phase("optimizer", kernels=10, host_us=PER_LAUNCH_US, gpu_us=300.0),
]

# A captured graph replays every kernel with one host call. The GPU work is unchanged.
ONE_GRAPH = [
    Phase("graph replay", kernels=1, host_us=PER_LAUNCH_US, gpu_us=15000.0),
]

VERSIONS = [
    ("as written: loss.item() mid-step, 1,000 optimizer launches", AS_WRITTEN),
    ("fix 1: log outside the step (no mid-step sync)", NO_MID_STEP_SYNC),
    ("fix 2: fix 1 + the optimizer as 10 launches", FEWER_LAUNCHES),
    ("alt 2: fix 1 + the whole step captured as one graph", ONE_GRAPH),
]

# The article's "Try it yourself" answers.
EXERCISES = [
    ("exercise 1: loss.item() moved after the optimizer", [
        Phase("forward", kernels=40, host_us=PER_LAUNCH_US, gpu_us=100.0),
        Phase("backward", kernels=80, host_us=PER_LAUNCH_US, gpu_us=100.0),
        Phase("optimizer", kernels=1000, host_us=PER_LAUNCH_US, gpu_us=3.0),
        Phase("loss.item()", sync=True),
    ]),
    ("exercise 2: as written, but each optimizer kernel takes 25 us", [
        Phase("forward", kernels=40, host_us=PER_LAUNCH_US, gpu_us=100.0),
        Phase("backward", kernels=80, host_us=PER_LAUNCH_US, gpu_us=100.0),
        Phase("loss.item()", sync=True),
        Phase("optimizer", kernels=1000, host_us=PER_LAUNCH_US, gpu_us=25.0),
    ]),
]

STEADY_STEPS = 20


def steady_state(phases):
    """Per-step period once the loop settles, read off GPU completion times."""
    results, _, host_end, gpu_end, busy = run(phases, steps=STEADY_STEPS)
    ends = [r.gpu_end_ms for r in results]
    period = ends[-1] - ends[-2]
    return {
        "period_ms": round(period, 3),
        "utilization_pct": round(100 * results[-1].busy_ms / period, 1),
        "naive_loop_ms_per_step": round(host_end / STEADY_STEPS, 3),
        "true_loop_ms_per_step": round(gpu_end / STEADY_STEPS, 3),
    }


def one_step(phases):
    results, trace, *_ = run(phases, steps=1)
    r = results[0]
    return {
        "naive_ms": {k: round(v, 3) for k, v in r.naive_ms.items()},
        "event_ms": {k: round(v, 3) for k, v in r.event_ms.items()},
        "kernel_ms": {k: round(v, 3) for k, v in r.kernel_ms.items()},
        "spans_ms": {k: [round(x, 3) for x in v] for k, v in r.spans.items()},
        "kernels_ms": r.kernels,
        "wall_ms": round(r.wall_ms, 3),
        "busy_ms": round(r.busy_ms, 3),
        "idle_ms": round(r.wall_ms - r.busy_ms, 3),
        "utilization_pct": round(100 * r.busy_ms / r.wall_ms, 1),
        "trace": trace,
    }


def fmt_table(name, step, steady):
    lines = [f"\n== {name}", f"   {'phase':<14}{'host timer':>12}{'CUDA events':>13}{'kernels ran':>13}"]
    for ph in step["naive_ms"]:
        lines.append(f"   {ph:<14}{step['naive_ms'][ph]:>10.2f} ms{step['event_ms'][ph]:>10.2f} ms"
                     f"{step['kernel_ms'][ph]:>10.2f} ms")
    lines.append(f"   one step, cold start : {step['wall_ms']:.2f} ms wall, "
                 f"{step['busy_ms']:.2f} ms of kernels, {step['idle_ms']:.2f} ms GPU idle "
                 f"({100 - step['utilization_pct']:.1f}% of the step)")
    lines.append(f"   steady state         : {steady['period_ms']:.2f} ms per step, "
                 f"utilization by nvidia-smi's definition {steady['utilization_pct']:.1f}%")
    lines.append(f"   {STEADY_STEPS}-step loop timed on the host, no final sync: "
                 f"{steady['naive_loop_ms_per_step']:.2f} ms/step reported, "
                 f"{steady['true_loop_ms_per_step']:.2f} ms/step true")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="print machine-readable results")
    ap.add_argument("--trace", action="store_true", help="print queue depth over one step")
    args = ap.parse_args()

    out = []
    for name, phases in VERSIONS + EXERCISES:
        out.append({"version": name, "step": one_step(phases), "steady": steady_state(phases)})

    if args.json:
        for item in out:
            item["step"].pop("kernels_ms")      # 1,120 intervals; the figures read them directly
        print(json.dumps(out, indent=2))
        return

    print("Model of one CUDA stream. Inputs are round numbers, not measurements.")
    print(f"Host cost per kernel launch: {PER_LAUNCH_US:.0f} us. Unbounded launch queue.")
    for item in out:
        print(fmt_table(item["version"], item["step"], item["steady"]))
        if args.trace and item is out[0]:
            print("\n   queue depth (kernels issued, not finished) at selected times:")
            trace = item["step"]["trace"]
            for t_ms in (0.5, 1.0, 2.4, 4.0, 8.0, 12.0, 12.5, 20.0, 31.9):
                depth = 0
                for t, d in trace:
                    if t <= t_ms:
                        depth = d
                print(f"     t = {t_ms:>5.1f} ms  depth {depth}")


if __name__ == "__main__":
    main()
