#!/usr/bin/env python3
"""Five causes of one "CUDA out of memory" error, reproduced on one GPU.

Grade G3: needs one NVIDIA GPU, a CUDA build of PyTorch (written against 2.15.0) and about 31 GiB
of free GPU memory; `--layers 8` halves every size. Each case trains the same stand-in model on an
emulated 24 GiB card (see Card), fails with PyTorch's real out-of-memory message, and where the
article shows a fix, applies it and runs again. Each case runs in a fresh process; this parent
process never touches CUDA, so it never appears in a message as "another process".

  python oom_lab.py run --out mine.json           # every case, about three minutes
  python oom_lab.py run --case fragmentation      # one case
  python oom_lab.py mystery --seed 3              # E4: one fault, not named
"""

import argparse
import collections
import contextlib
import ctypes
import datetime
import json
import os
import pathlib
import platform
import random
import signal
import subprocess
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
GiB, MiB = 2**30, 2**20
WIDTH = 8192          # every layer is Linear(8192, 8192): 256 MiB of fp32 weights
LAYERS = 16           # 16 layers: 4 GiB of weights, 16 GiB with gradients and Adam's two states
BATCH = 6144          # rows per training step: two 192 MiB activations saved per layer
VAL_BATCH = 1536      # rows per validation batch: 1.5 GiB of saved activations at 16 layers
VAL_BATCHES = 12
CARD_GIB, HOLDER_GIB, POOL_GIB, CPU_GIB = 24, 6, 4, 8   # all scaled by --layers / 16
EXPANDABLE = {"PYTORCH_ALLOC_CONF": "expandable_segments:True"}
# Settings that change what the allocator or the context does. Workers start without them, so a
# value exported in your shell cannot silently change a result; cases that need one set it.
CLEARED_ENV = ("PYTORCH_CUDA_ALLOC_CONF", "PYTORCH_ALLOC_CONF", "PYTORCH_HIP_ALLOC_CONF",
               "PYTORCH_NO_CUDA_MEMORY_CACHING", "CUDA_MODULE_LOADING", "CUBLAS_WORKSPACE_CONFIG",
               "TORCH_CUBLAS_WORKSPACE_CACHE", "CUDA_LAUNCH_BLOCKING")
STAT_KEYS = ("allocated_bytes.all.current", "allocated_bytes.all.peak", "reserved_bytes.all.current",
             "reserved_bytes.all.peak", "inactive_split_bytes.all.current", "inactive_split.all.current",
             "segment.all.current", "num_alloc_retries", "num_ooms", "num_device_alloc", "num_device_free")

# Each case: what the worker runs and the environment it starts with. The article's five failures
# are fragmentation, capacity, retained, other-process and non-pytorch.
CASES = {
    "provenance": {},
    "baseline": {"batch": BATCH, "steps": 3},
    "fragmentation": {"batch": 2 * BATCH, "steps": 3, "retry": True},
    "capacity": {"batch": 2 * BATCH, "steps": 3, "env": EXPANDABLE, "retry": True},
    "capacity-fix": {"batch": 2 * BATCH, "steps": 3, "env": EXPANDABLE, "checkpoint": 4},
    "retained": {},
    "retained-fix": {"no_grad": True},
    "other-process": {},
    "other-process-fix": {"fix": True},
    "non-pytorch": {},
    "non-pytorch-fix": {"fix": True},
    "inventory": {},
    "inventory-eager": {"env": {"CUDA_MODULE_LOADING": "EAGER"}},
    "unified": {},
    "zombie": {},
    "precedence-a": {"env": {"PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:False",
                             "PYTORCH_ALLOC_CONF": "expandable_segments:True"}},
    "precedence-b": {"env": {"PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
                             "PYTORCH_ALLOC_CONF": "expandable_segments:False"}},
}
FAULTS = ("fragmentation", "capacity", "retained", "other-process", "non-pytorch")


# ------------------------------------------------------------------ NVML, read through ctypes
class _ProcInfo(ctypes.Structure):
    _fields_ = [("pid", ctypes.c_uint), ("used", ctypes.c_ulonglong),
                ("gpu_instance", ctypes.c_uint), ("compute_instance", ctypes.c_uint)]


class _MemInfo(ctypes.Structure):
    _fields_ = [("total", ctypes.c_ulonglong), ("free", ctypes.c_ulonglong), ("used", ctypes.c_ulonglong)]


class Nvml:
    """The few NVML calls this lab needs: per-process usage is what PyTorch's message prints."""

    NOT_AVAILABLE = 0xFFFFFFFFFFFFFFFF

    def __init__(self):
        self.lib = ctypes.CDLL("libnvidia-ml.so.1")
        if self.lib.nvmlInit_v2() != 0:
            raise RuntimeError("nvmlInit_v2 failed")

    def device(self, uuid=None):
        handle = ctypes.c_void_p()
        rc = (self.lib.nvmlDeviceGetHandleByUUID(uuid.encode(), ctypes.byref(handle)) if uuid
              else self.lib.nvmlDeviceGetHandleByIndex_v2(0, ctypes.byref(handle)))
        if rc != 0:
            raise RuntimeError(f"no NVML handle for {uuid or 'device 0'} (rc {rc})")
        return handle

    def processes(self, handle, kind="Compute"):
        """{pid: bytes in use}; None when the platform does not report it."""
        fn = getattr(self.lib, f"nvmlDeviceGet{kind}RunningProcesses_v3")
        for size in (16, 128, 1024):
            arr, n = (_ProcInfo * size)(), ctypes.c_uint(size)
            rc = fn(handle, ctypes.byref(n), arr)
            if rc == 0:
                return {a.pid: (None if a.used == self.NOT_AVAILABLE else a.used) for a in arr[:n.value]}
            if rc != 7:  # 7 is NVML_ERROR_INSUFFICIENT_SIZE: retry with a larger array
                return None
        return None

    def memory_info(self, handle):
        m = _MemInfo()
        rc = self.lib.nvmlDeviceGetMemoryInfo(handle, ctypes.byref(m))
        return {"rc": rc, "total": m.total if rc == 0 else None, "used": m.used if rc == 0 else None}

    def versions(self):
        buf, umd = ctypes.create_string_buffer(96), ctypes.c_int(0)
        kmd = buf.value.decode() if self.lib.nvmlSystemGetDriverVersion(buf, 96) == 0 else None
        ceiling = umd.value if self.lib.nvmlSystemGetCudaDriverVersion_v2(ctypes.byref(umd)) == 0 else None
        return kmd, ceiling


# ------------------------------------------------------------------ provenance
def cpu_model():
    try:
        out = subprocess.run(["lscpu"], capture_output=True, text=True, check=True).stdout
        names = [line.split(":", 1)[1].strip() for line in out.splitlines() if line.startswith("Model name")]
        if names:
            return " + ".join(dict.fromkeys(names))
    except (OSError, subprocess.CalledProcessError):
        pass
    return platform.processor() or platform.machine()


def system_name():
    parts = []
    for f in ("sys_vendor", "product_name"):
        try:
            parts.append(pathlib.Path(f"/sys/class/dmi/id/{f}").read_text())
        except OSError:
            pass
    return " ".join(" ".join(parts).split()) or None  # DMI strings carry padding spaces


def provenance(nvml):
    import torch

    props = torch.cuda.get_device_properties(0)
    kmd, umd = nvml.versions()
    versions = {"torch": torch.__version__, "torch_cuda_runtime": torch.version.cuda}
    for mod in ("cuda.bindings", "numpy"):
        with contextlib.suppress(ImportError):
            versions[mod] = __import__(mod, fromlist=["__version__"]).__version__
    os_name = None
    with contextlib.suppress(OSError):
        for line in pathlib.Path("/etc/os-release").read_text().splitlines():
            if line.startswith("PRETTY_NAME="):
                os_name = line.split("=", 1)[1].strip('"')
    return {
        "captured_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "gpu_name": props.name, "compute_capability": f"sm_{props.major}{props.minor}",
        "sm_count": props.multi_processor_count, "integrated": bool(props.is_integrated),
        "device_total_bytes": props.total_memory, "kmd_version": kmd, "cuda_umd_version": umd,
        "versions": versions, "cpu_model": cpu_model(), "python_version": platform.python_version(),
        "os": os_name, "kernel": platform.release(), "instance": system_name(),
    }


def provenance_line(p):
    umd = p["cuda_umd_version"]
    umd = f"{umd // 1000}.{umd % 1000 // 10}" if umd else "?"
    memory = " unified" if p["integrated"] else ""
    return (f"Captured {p['captured_at_utc']} on {p['gpu_name']} ({p['compute_capability']}, "
            f"{p['sm_count']} SMs, {p['device_total_bytes'] / GiB:.2f} GiB{memory}), KMD {p['kmd_version']}, "
            f"CUDA UMD {umd}, torch {p['versions']['torch']} (runtime {p['versions']['torch_cuda_runtime']}), "
            f"{p['cpu_model']}, Python {p['python_version']}, {p['os']}, {p['instance']}.")


# ------------------------------------------------------------------ the emulated card
class Card:
    """A card of `capacity` bytes, emulated on a GPU that has more memory than that.

    A real card's driver refuses an allocation when the card is full, whoever filled it. Here
    PyTorch's per-process memory fraction plays the driver: before every phase of a step, sync()
    sets PyTorch's allowance to the capacity, minus what NVML says other compute processes hold,
    minus what this process holds outside PyTorch's allocator. The allocator, its cache, its block
    splitting and its out-of-memory message are all real; only the size of the card is emulated,
    which is why every message carries an "N GiB allowed;" clause a physical card does not print.
    """

    def __init__(self, capacity, nvml):
        import torch

        self.torch, self.nvml, self.capacity, self.pid = torch, nvml, capacity, os.getpid()
        self.handle = nvml.device("GPU-" + str(torch.cuda.get_device_properties(0).uuid))
        self.total = torch.cuda.mem_get_info()[1]
        self.emulated = capacity < self.total  # on a card no larger than this, the driver decides

    def ledger(self):
        torch = self.torch
        procs = self.nvml.processes(self.handle) or {}
        own = procs.get(self.pid) or 0
        others = {pid: used for pid, used in procs.items() if pid != self.pid and used}
        reserved, allocated = torch.cuda.memory_reserved(), torch.cuda.memory_allocated()
        non_pytorch = max(own - reserved, 0)
        free, total = torch.cuda.mem_get_info()
        return {"capacity": self.capacity, "allowed": self.capacity - sum(others.values()) - non_pytorch,
                "others": others, "this_process": own, "reserved": reserved, "allocated": allocated,
                "non_pytorch": non_pytorch, "device_free": free, "device_total": total}

    def sync(self):
        ledger = self.ledger()
        if self.emulated:
            self.torch.cuda.set_per_process_memory_fraction(max(ledger["allowed"], 0) / self.total)
        return ledger


# ------------------------------------------------------------------ the stand-in model
def build(layers):
    import torch

    torch.set_float32_matmul_precision("high")  # TF32 matmuls: faster, and no change to any tensor's size
    torch.manual_seed(0)
    blocks = []
    for _ in range(layers):
        blocks += [torch.nn.Linear(WIDTH, WIDTH, bias=False, device="cuda"), torch.nn.GELU()]
    model = torch.nn.Sequential(*blocks)
    return model, torch.optim.Adam(model.parameters(), lr=1e-4)  # foreach: the CUDA default


def warm_up():
    """Run one tiny step first, so the kernels every case uses are loaded before the ledger is read:
    with lazy loading the context grows as modules load, and that growth is not a cause."""
    import torch

    model = torch.nn.Sequential(torch.nn.Linear(256, 256, bias=False, device="cuda"), torch.nn.GELU())
    opt = torch.optim.Adam(model.parameters(), lr=1e-4)
    model(torch.randn(64, 256, device="cuda")).square().mean().backward()
    opt.step()
    torch.cuda.synchronize()


def summarize_snapshot():
    """The allocator's segments at this moment: enough to find the slivers without a viewer."""
    import torch

    sizes, segments = collections.Counter(), []
    largest = in_partly_used = in_empty = 0
    for seg in torch.cuda.memory_snapshot():
        blocks = seg["blocks"]
        free = [b["size"] for b in blocks if b["state"] == "inactive"]
        sizes.update(free)
        if any(b["state"] != "inactive" for b in blocks):
            in_partly_used += sum(free)
        else:
            in_empty += sum(free)
        largest = max([largest, *free])
        segments.append({"total": seg["total_size"], "allocated": seg["allocated_size"],
                         "blocks": len(blocks), "largest_free": max(free, default=0),
                         "pool": seg["segment_type"], "expandable": bool(seg.get("is_expandable"))})
    return {"segments": segments, "free_block_sizes": {str(k): v for k, v in sorted(sizes.items())},
            "largest_free_block": largest, "free_in_partly_used_segments": in_partly_used,
            "free_in_empty_segments": in_empty}


def capture_oom(err, card, **where):
    """Everything about the failure, read in the except block. By then the failed operation has
    unwound: any partial outputs it had made (the first tensors of a foreach list) are free again,
    and the snapshot shows them as empty segments."""
    import torch

    stats = torch.cuda.memory_stats()
    record = {"message": str(err), **where, "stats": {k: stats.get(k) for k in STAT_KEYS},
              "snapshot": summarize_snapshot(), "ledger": card.ledger()}
    print(f"    OOM at {where}: {str(err)[:96]}...", flush=True)
    return record


def retry_after_empty_cache(phase_fn, card):
    """The usual first reflex: empty the cache and try the failed phase again."""
    import torch

    before = torch.cuda.memory_reserved()
    torch.cuda.empty_cache()
    result = {"released": before - torch.cuda.memory_reserved()}
    card.sync()
    try:
        phase_fn()
        result["failed"] = False
    except torch.OutOfMemoryError as err:
        result.update(failed=True, message=str(err))
    print(f"    empty_cache() released {result['released'] / MiB:.0f} MiB; retry failed: {result['failed']}",
          flush=True)
    return result


def train(model, opt, card, batch, steps, record, *, checkpoint=0, running_loss=False, key="trace",
          retry=False):
    """Train `steps` steps; on an out-of-memory error, record it and return False."""
    import torch
    from torch.utils.checkpoint import checkpoint_sequential

    trace, running = record.setdefault(key, []), None
    for step in range(steps):
        card.sync()
        t0, peaks, live = time.perf_counter(), {}, {}
        point = {"step": step, "batch": batch, "allocated": torch.cuda.memory_allocated(),
                 "reserved": torch.cuda.memory_reserved()}

        def forward():
            live.clear()  # a retried forward must not hold the first attempt's input too
            x = torch.randn(batch, WIDTH, device="cuda")
            out = checkpoint_sequential(model, checkpoint, x, use_reentrant=False) if checkpoint else model(x)
            live["loss"] = out.square().mean()

        phases = {"forward": forward, "backward": lambda: live["loss"].backward(), "optimizer": opt.step}
        try:
            for phase, fn in phases.items():
                card.sync()
                torch.cuda.reset_peak_memory_stats()
                fn()
                peaks[phase] = torch.cuda.max_memory_allocated()
            opt.zero_grad(set_to_none=True)
            if running_loss:  # the FAQ's pattern: keeps a tensor with history from every step
                running = live["loss"] if running is None else running + live["loss"]
        except torch.OutOfMemoryError as err:
            record["oom"] = capture_oom(err, card, step=step, phase=phase, batch=batch)
            del err  # release the traceback's frames before retrying
            if retry:
                record["retry_after_empty_cache"] = retry_after_empty_cache(phases[phase], card)
            trace.append({**point, "peaks": peaks, "oom": True})
            return False
        live.clear()
        torch.cuda.synchronize()
        trace.append({**point, "peaks": peaks, "end_allocated": torch.cuda.memory_allocated(),
                      "seconds": round(time.perf_counter() - t0, 3)})
        print(f"    step {step} batch {batch}: allocated {point['allocated'] / GiB:.2f} GiB at start, "
              f"peak {max(peaks.values()) / GiB:.2f} GiB", flush=True)
    return True


def validate(model, card, batches, record, *, no_grad, batch=VAL_BATCH):
    """Evaluate `batches` batches, accumulating the loss; on out-of-memory, record it."""
    import torch

    trace = record.setdefault("val_trace", [])
    total = 0.0
    with torch.no_grad() if no_grad else contextlib.nullcontext():
        for k in range(batches):
            card.sync()
            point = {"batch_index": k, "allocated": torch.cuda.memory_allocated()}
            try:
                loss = model(torch.randn(batch, WIDTH, device="cuda")).square().mean()
                # The bug and its fix differ in one place: grad mode, and .item() instead of the tensor.
                total = total + (loss.item() if no_grad else loss)
            except torch.OutOfMemoryError as err:
                record["oom"] = capture_oom(err, card, step=k, phase="validation", batch=batch)
                trace.append({**point, "oom": True})
                return False
            trace.append(point)
    print(f"    validation: {batches} batches, allocated {trace[0]['allocated'] / GiB:.2f} -> "
          f"{trace[-1]['allocated'] / GiB:.2f} GiB", flush=True)
    return True


# ------------------------------------------------------------------ helper processes
def cmd_hold(args):
    """Hold `--bytes` of GPU memory: the second process of the other-process and zombie cases."""
    import torch

    held = torch.empty(args.bytes, dtype=torch.uint8, device="cuda")
    torch.cuda.synchronize()
    pathlib.Path(args.ready).write_text(json.dumps({"pid": os.getpid(), "ppid": os.getppid()}))
    if args.exit:  # the zombie case: exit at once, and let the parent not reap us
        return
    deadline = time.time() + args.timeout  # a holder never outlives its timeout, even orphaned
    while time.time() < deadline:
        time.sleep(0.2)
    del held


def cmd_launch_orphan(args):
    """Start a holder in its own session and exit at once, so the holder is left an orphan."""
    subprocess.Popen([sys.executable, str(HERE / "oom_lab.py"), "hold", "--bytes", str(args.bytes),
                      "--ready", args.ready, "--timeout", str(args.timeout)],
                     start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)


def wait_for(path, timeout=60.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if path.exists() and path.read_text():
            return json.loads(path.read_text())
        time.sleep(0.1)
    raise TimeoutError(f"no {path.name} after {timeout} s")


def proc_status(pid):
    """State and parent of a process, read from /proc like ps does."""
    try:
        stat = pathlib.Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return None
    fields = stat[stat.rindex(")") + 2:].split()
    return {"pid": pid, "state": fields[0], "ppid": int(fields[1])}


def stop(pid, timeout=30.0):
    """SIGTERM a process and wait until it is gone (an orphan is not our child: poll /proc)."""
    with contextlib.suppress(ProcessLookupError):
        os.kill(pid, signal.SIGTERM)
    deadline = time.time() + timeout
    while proc_status(pid) and (proc_status(pid) or {}).get("state") != "Z" and time.time() < deadline:
        time.sleep(0.05)


def proc_comm(pid):
    with contextlib.suppress(OSError):
        return pathlib.Path(f"/proc/{pid}/comm").read_text().strip()
    return None


# ------------------------------------------------------------------ the cases
def case_train(cfg, record, nvml):
    card = Card(cfg["card"], nvml)
    model, opt = build(cfg["layers"])
    record["ledger_start"] = card.sync()
    record["completed"] = train(model, opt, card, cfg["batch"], cfg["steps"], record,
                                checkpoint=cfg.get("checkpoint", 0), retry=cfg.get("retry", False))


def case_retained(cfg, record, nvml):
    card = Card(cfg["card"], nvml)
    model, opt = build(cfg["layers"])
    record["ledger_start"] = card.sync()
    # Two training steps with the FAQ's `running_loss += loss`: backward() has already freed each
    # step's saved tensors, so this costs almost nothing. The same habit in validation does not.
    train(model, opt, card, BATCH, 2, record, running_loss=True)
    record["completed"] = validate(model, card, VAL_BATCHES, record, no_grad=cfg.get("no_grad", False),
                                   batch=cfg["val_batch"])


def case_other_process(cfg, record, nvml, fix=False):
    ready = pathlib.Path(cfg["run_dir"]) / f"holder-{os.getpid()}.json"  # one per worker: never a stale file
    subprocess.run([sys.executable, str(HERE / "oom_lab.py"), "launch-orphan", "--bytes", str(cfg["holder"]),
                    "--ready", str(ready), "--timeout", "240"], check=True)
    holder = wait_for(ready)
    time.sleep(0.5)  # let the launcher's exit reparent the holder before we look
    record["holder"] = {**holder, "now": proc_status(holder["pid"]), "comm": proc_comm(holder["pid"]),
                        "parent_comm": None}
    record["holder"]["parent_comm"] = proc_comm(record["holder"]["now"]["ppid"]) if record["holder"]["now"] else None
    try:
        if fix:  # the fix: stop the process the message names, then train
            stop(holder["pid"])
        card = Card(cfg["card"], nvml)
        model, opt = build(cfg["layers"])
        record["ledger_start"] = card.sync()
        record["completed"] = train(model, opt, card, BATCH, 2, record)
    finally:
        stop(holder["pid"])


def case_non_pytorch(cfg, record, nvml, fix=False):
    import torch
    from cuda.bindings import driver

    torch.empty(1, device="cuda")  # PyTorch's primary context becomes current; the pool lands in it
    # A stand-in for any library that manages device memory itself: a data-loading or preprocessing
    # library's pool, another framework, a communication library. PyTorch's counters never see it.
    err, pool = driver.cuMemAlloc(cfg["pool"])
    if err != driver.CUresult.CUDA_SUCCESS:
        raise RuntimeError(f"cuMemAlloc failed: {err}")
    record["pool_bytes"] = cfg["pool"]
    try:
        if fix:  # the fix: release the library's memory, then train
            driver.cuMemFree(pool)
            pool = None
        card = Card(cfg["card"], nvml)
        model, opt = build(cfg["layers"])
        record["ledger_start"] = card.sync()
        record["completed"] = train(model, opt, card, BATCH, 2, record)
    finally:
        if pool is not None:
            driver.cuMemFree(pool)


def case_inventory(cfg, record, nvml):
    """What this process holds outside PyTorch's allocator, stage by stage."""
    import torch
    import torch.distributed as dist

    card, stages = None, record.setdefault("stages", [])

    def stage(name):
        torch.cuda.synchronize()
        ledger = card.ledger()
        stages.append({"stage": name, "non_pytorch": ledger["non_pytorch"],
                       "this_process": ledger["this_process"], "reserved": ledger["reserved"]})
        print(f"    {name:52s} outside PyTorch {ledger['non_pytorch'] / MiB:8.1f} MiB", flush=True)

    torch.empty(1, device="cuda")
    card = Card(cfg["card"], nvml)
    stage("CUDA context and one tensor")
    a = torch.randn(4096, 4096, device="cuda")
    b = a @ a
    stage("+ first cuBLAS matrix multiply")
    if os.environ.get("CUDA_MODULE_LOADING") == "EAGER":
        return
    warm_up()
    stage("+ the training step's kernels (GELU, Adam)")
    conv = torch.nn.Conv2d(64, 64, 3, device="cuda")
    conv(torch.randn(8, 64, 64, 64, device="cuda"))
    stage("+ first cuDNN convolution")
    store = dist.FileStore(str(pathlib.Path(cfg["run_dir"]) / "nccl-store"), 1)
    dist.init_process_group("nccl", store=store, rank=0, world_size=1, device_id=torch.device("cuda:0"))
    stage("+ NCCL communicator, one rank")
    dist.all_reduce(torch.ones(1024, device="cuda"))
    stage("+ first all_reduce")
    dist.destroy_process_group()
    stage("after destroy_process_group()")
    del a, b


def read_meminfo():
    out = {}
    with contextlib.suppress(OSError):
        for line in pathlib.Path("/proc/meminfo").read_text().splitlines():
            key, value = line.split(":", 1)
            if key in ("MemTotal", "MemFree", "MemAvailable", "Cached"):
                out[key] = int(value.split()[0]) * 1024
    return out


def case_unified(cfg, record, nvml):
    """What a GPU that shares memory with the CPU reports, and what a CPU allocation does to it."""
    import torch

    torch.empty(1, device="cuda")
    card = Card(cfg["card"], nvml)
    record["integrated"] = bool(torch.cuda.get_device_properties(0).is_integrated)
    record["nvml_memory_info"] = nvml.memory_info(card.handle)
    graphics = nvml.processes(card.handle, "Graphics") or {}
    record["graphics_processes"] = {str(p): {"used": u, "comm": proc_comm(p)} for p, u in graphics.items()}

    def look(label):
        free, total = torch.cuda.mem_get_info()
        own = (nvml.processes(card.handle) or {}).get(os.getpid())
        record.setdefault("looks", []).append({"label": label, "cuda_free": free, "cuda_total": total,
                                               "nvml_this_process": own, **read_meminfo()})

    look("start")
    if not record["integrated"]:
        return  # on a discrete card CPU memory is a different pool; nothing to show
    cpu = torch.ones(cfg["cpu"], dtype=torch.uint8)  # CPU memory, every page written
    look(f"after a {cfg['cpu'] / GiB:.0f} GiB CPU tensor")
    del cpu
    time.sleep(1.0)
    look("after freeing it")


def case_zombie(cfg, record, nvml):
    """A process that exited but was never reaped is a zombie (state Z). Does it still hold memory?
    This worker opens no CUDA context of its own; it only watches the child through NVML."""
    handle = nvml.device()
    ready = pathlib.Path(cfg["run_dir"]) / f"zombie-{os.getpid()}.json"
    child = subprocess.Popen([sys.executable, str(HERE / "oom_lab.py"), "hold", "--bytes", str(cfg["holder"]),
                              "--ready", str(ready), "--exit"])
    wait_for(ready)
    t0, base, timeline, last = time.time(), read_meminfo().get("MemFree"), [], None
    while time.time() - t0 < 10:  # watch without reaping: state, NVML's view, and free memory
        state = (proc_status(child.pid) or {}).get("state")
        used = (nvml.processes(handle) or {}).get(child.pid)
        row = (state, used is not None, used)
        if row != last:
            timeline.append({"t": round(time.time() - t0, 3), "state": state, "listed_by_nvml": used is not None,
                             "used": used, "memfree_delta": read_meminfo().get("MemFree", 0) - (base or 0)})
            last = row
        if state == "Z" and used is None:
            break
        time.sleep(0.01)
    record["timeline"] = timeline
    record["child"] = proc_status(child.pid)
    child.wait()  # reap it only now
    record["after_reap_listed"] = child.pid in (nvml.processes(handle) or {})


def case_precedence(cfg, record, nvml):
    import torch

    torch.empty(64 * MiB, dtype=torch.uint8, device="cuda")
    record["env"] = {k: os.environ.get(k) for k in ("PYTORCH_CUDA_ALLOC_CONF", "PYTORCH_ALLOC_CONF")}
    record["expandable_segments_active"] = any(s.get("is_expandable") for s in torch.cuda.memory_snapshot())


def run_case(name, cfg, record, nvml, fix=False):
    if name == "provenance":
        import torch

        torch.empty(1, device="cuda")
        record["provenance"] = provenance(nvml)
    elif name in ("baseline", "fragmentation", "capacity", "capacity-fix"):
        warm_up()
        case_train(cfg, record, nvml)
    elif name in ("retained", "retained-fix"):
        warm_up()
        case_retained(cfg, record, nvml)
    elif name in ("other-process", "other-process-fix"):
        warm_up()
        case_other_process(cfg, record, nvml, fix=fix)
    elif name in ("non-pytorch", "non-pytorch-fix"):
        warm_up()
        case_non_pytorch(cfg, record, nvml, fix=fix)
    elif name.startswith("inventory"):
        case_inventory(cfg, record, nvml)
    elif name == "unified":
        case_unified(cfg, record, nvml)
    elif name == "zombie":
        case_zombie(cfg, record, nvml)
    elif name.startswith("precedence"):
        case_precedence(cfg, record, nvml)
    else:
        raise SystemExit(f"unknown case {name}")


def cmd_worker(args):
    cfg = json.loads(args.config)
    record = {"case": args.case, "env": {k: os.environ[k] for k in CLEARED_ENV if k in os.environ},
              "config": {k: v for k, v in cfg.items() if k != "run_dir"}}
    run_case(args.case, cfg, record, Nvml(), fix=cfg.get("fix", False))
    pathlib.Path(args.record).write_text(json.dumps(record))


# ------------------------------------------------------------------ orchestration (no CUDA here)
def sizes(layers, val_batch=VAL_BATCH):
    scale = layers / LAYERS
    return {"layers": layers, "val_batch": val_batch, "card": int(CARD_GIB * GiB * scale),
            "holder": int(HOLDER_GIB * GiB * scale), "pool": int(POOL_GIB * GiB * scale),
            "cpu": int(CPU_GIB * GiB * scale)}


def run_worker(name, base, run_dir, extra=None):
    spec = dict(CASES[name])
    env = {k: v for k, v in os.environ.items() if k not in CLEARED_ENV}
    env.update(spec.pop("env", {}))
    cfg = {**base, **spec, **(extra or {}), "run_dir": str(run_dir)}
    out = run_dir / f"{name}.json"
    proc = subprocess.run([sys.executable, "-u", str(HERE / "oom_lab.py"), "worker", name,
                           "--config", json.dumps(cfg), "--record", str(out)], env=env, timeout=900)
    if proc.returncode != 0:
        return {"case": name, "error": f"worker exited with {proc.returncode}"}
    return json.loads(out.read_text())


def sweep_holders():
    """Stop any holder this lab started that is still alive, so it cannot leak into the next case."""
    for entry in pathlib.Path("/proc").iterdir():
        if entry.name.isdigit():
            with contextlib.suppress(OSError):
                cmd = (entry / "cmdline").read_bytes().split(b"\0")
                if any(c.endswith(b"oom_lab.py") for c in cmd) and b"hold" in cmd:
                    stop(int(entry.name))


def summarize(name, rec, card):
    import diagnose  # the G1 decision tree, from the same folder

    print(f"== {name}", flush=True)
    if "error" in rec:
        print(f"   ERROR: {rec['error']}")
        return
    oom = rec.get("oom")
    if oom:
        trace = rec.get("val_trace") or rec.get("trace") or []
        verdict = diagnose.diagnose(diagnose.parse_message(oom["message"]), card=card,
                                    growth=diagnose.growth_from_trace(trace))
        rec["verdict"] = verdict
        print(f"   OOM at {oom['phase']} of step {oom['step']} (batch {oom['batch']})")
        print("   " + oom["message"])
        print("   " + diagnose.explain(name, verdict).replace("\n", "\n   "))
        retry = rec.get("retry_after_empty_cache")
        if retry:
            print(f"   empty_cache() then the same {oom['phase']} again: released "
                  f"{diagnose.fmt(retry['released'])}, failed again: {retry['failed']}")
    else:
        if rec.get("trace"):
            t = rec["trace"]
            peak = max(max(s["peaks"].values()) for s in t)
            print(f"   completed {len(t)} steps of batch {t[0]['batch']}, peak allocated {diagnose.fmt(peak)}")
        if rec.get("val_trace"):
            v = rec["val_trace"]
            print(f"   completed {len(v)} validation batches, allocated at batch start "
                  f"{diagnose.fmt(v[0]['allocated'])} -> {diagnose.fmt(v[-1]['allocated'])}")
    for s in rec.get("stages", []):
        print(f"   {s['stage']:52s} outside PyTorch {diagnose.fmt(s['non_pytorch'])}")
    for look in rec.get("looks", []):
        print(f"   {look['label']:28s} CUDA free {diagnose.fmt(look['cuda_free'])}, "
              f"MemFree {diagnose.fmt(look.get('MemFree'))}, MemAvailable {diagnose.fmt(look.get('MemAvailable'))}")
    for row in rec.get("timeline", []):
        print(f"   t={row['t']:6.3f} s  state {row['state']}  listed by NVML: {row['listed_by_nvml']}  "
              f"MemFree {diagnose.fmt(row['memfree_delta'])} vs the start")
    if "timeline" in rec:
        print(f"   reaped afterwards; listed by NVML after reaping: {rec['after_reap_listed']}")
    if "expandable_segments_active" in rec:
        print(f"   {rec['env']} -> expandable segments active: {rec['expandable_segments_active']}")


def cmd_run(args):
    sys.path.insert(0, str(HERE))
    base = sizes(args.layers, args.val_batch)
    names = [n for n in CASES if n != "provenance"] if args.case == "all" else [args.case]
    out = {"schema": 1, "card_bytes": base["card"], "config": {**base, "width": WIDTH, "batch": BATCH,
           "val_batches": VAL_BATCHES}, "runs": {}}
    with tempfile.TemporaryDirectory(prefix="oom-lab-", dir=HERE) as tmp:
        run_dir = pathlib.Path(tmp)
        try:
            out["provenance"] = run_worker("provenance", base, run_dir)["provenance"]
            print(provenance_line(out["provenance"]), flush=True)
            for name in names:
                print(f"-- running {name}", flush=True)
                out["runs"][name] = run_worker(name, base, run_dir)
                sweep_holders()
                summarize(name, out["runs"][name], base["card"])
        finally:
            sweep_holders()
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + "\n")
    print(f"wrote {args.out}")


def cmd_mystery(args):
    """E4: run one of the five faults without naming it. --fix applies one cause's fix."""
    sys.path.insert(0, str(HERE))
    fault = random.Random(args.seed).choice(FAULTS)
    if args.reveal:
        print(f"seed {args.seed}: {fault}")
        return
    base = sizes(args.layers)
    extra, name = {}, fault
    if args.fix == fault:  # the right fix for this fault
        name = {"fragmentation": "capacity", "capacity": "capacity-fix", "retained": "retained-fix",
                "other-process": "other-process-fix", "non-pytorch": "non-pytorch-fix"}[fault]
        if fault == "fragmentation":
            extra = {"steps": 1}  # expandable segments: the first step now completes
    with tempfile.TemporaryDirectory(prefix="oom-lab-", dir=HERE) as tmp:
        try:
            rec = run_worker(name, base, pathlib.Path(tmp), extra)
        finally:
            sweep_holders()
    oom = rec.get("oom")
    if not oom:
        print(f"completed without running out of memory (fix: {args.fix})")
        return
    print(oom["message"])
    print("allocated at the start of each iteration (GiB):",
          [round(t["allocated"] / GiB, 2) for t in (rec.get("val_trace") or rec.get("trace") or [])])
    print("compute processes on the GPU at the failure:",
          {pid: f"{used / GiB:.2f} GiB" for pid, used in oom["ledger"]["others"].items()} or "only this one")
    print(f"card capacity: {base['card'] / GiB:.2f} GiB (emulated)")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="run cases and write a captures file")
    run.add_argument("--case", default="all", choices=["all", *[n for n in CASES if n != "provenance"]])
    run.add_argument("--out", default="mine.json", help="never the shipped captures.json")
    run.add_argument("--layers", type=int, default=LAYERS, help="16 needs about 31 GiB free; 8 halves it")
    run.add_argument("--val-batch", type=int, default=VAL_BATCH, help="rows per validation batch (E3)")
    mys = sub.add_parser("mystery", help="E4: one unnamed fault")
    mys.add_argument("--seed", type=int, required=True)
    mys.add_argument("--fix", choices=FAULTS, help="apply this cause's fix and run again")
    mys.add_argument("--reveal", action="store_true", help="print which fault the seed picks")
    mys.add_argument("--layers", type=int, default=LAYERS)
    wrk = sub.add_parser("worker", help=argparse.SUPPRESS)
    wrk.add_argument("case")
    wrk.add_argument("--config", required=True)
    wrk.add_argument("--record", required=True)
    hold = sub.add_parser("hold", help=argparse.SUPPRESS)
    hold.add_argument("--bytes", type=int, required=True)
    hold.add_argument("--ready", required=True)
    hold.add_argument("--timeout", type=float, default=240)
    hold.add_argument("--exit", action="store_true")
    orphan = sub.add_parser("launch-orphan", help=argparse.SUPPRESS)
    orphan.add_argument("--bytes", type=int, required=True)
    orphan.add_argument("--ready", required=True)
    orphan.add_argument("--timeout", type=float, default=240)
    args = ap.parse_args()
    {"run": cmd_run, "mystery": cmd_mystery, "worker": cmd_worker, "hold": cmd_hold,
     "launch-orphan": cmd_launch_orphan}[args.cmd](args)


if __name__ == "__main__":
    main()
