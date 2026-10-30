#!/usr/bin/env python3
"""Name the cause of a PyTorch "CUDA out of memory" error from the numbers in its message.

Grade G1: standard library only, no GPU. It applies the article's decision tree, in this order:

  1. retained graph PyTorch's own allocation grows from one iteration to the next
  2. fragmentation  PyTorch already holds at least the request, free, but in pieces
  3. other process  the missing bytes are held by another process on the device
  4. non-PyTorch    the missing bytes are held by this process outside PyTorch's allocator
  5. capacity       none of the above: the workload needs more than the card has

Growth goes first because a leak also fragments: once it has eaten the headroom, the last few
small requests fail among slivers, and the message alone then reads like fragmentation.

  python diagnose.py captures.json                       # the article's runs, no GPU needed
  python diagnose.py --message-file oom.txt              # your own message
  python diagnose.py --message-file oom.txt --card 24GiB --growth 1.5GiB
"""

import argparse
import json
import pathlib
import re
import sys

UNITS = {"bytes": 1, "KiB": 2**10, "MiB": 2**20, "GiB": 2**30, "TiB": 2**40}
SIZE = r"([0-9][0-9.]*) (bytes|KiB|MiB|GiB|TiB)"
GiB = 2**30


def to_bytes(number, unit):
    return round(float(number) * UNITS[unit])


def parse_size(text):
    """'24GiB', '24 GiB' or a byte count -> bytes."""
    m = re.fullmatch(r"\s*([0-9][0-9.]*)\s*(bytes|KiB|MiB|GiB|TiB)?\s*", text)
    if not m:
        raise argparse.ArgumentTypeError(f"not a size: {text!r}")
    return to_bytes(m.group(1), m.group(2) or "bytes")


def fmt(n):
    """Print bytes the way PyTorch's message does, so the two can be compared by eye."""
    if n is None:
        return "?"
    sign, n = ("-" if n < 0 else ""), abs(n)
    if n <= 1024:
        return f"{sign}{n} bytes"
    for unit, scale in (("KiB", 2**10), ("MiB", 2**20), ("GiB", 2**30)):
        if n <= scale * 1024 or unit == "GiB":
            return f"{sign}{n / scale:.2f} {unit}"


def parse_message(message):
    """Pull every number out of PyTorch's out-of-memory message (format of torch 2.1 to 2.15)."""
    def one(pattern):
        m = re.search(pattern, message)
        return to_bytes(m.group(1), m.group(2)) if m else None

    fields = {
        "requested": one(r"Tried to allocate " + SIZE),
        "total": one(r"has a total capacity of " + SIZE),
        "free": one(r"of which " + SIZE + r" is free"),
        "this_process": one(r"this process has " + SIZE + r" memory in use"),
        "allowed": one(SIZE + r" allowed;"),
        "allocated": one(r"Of the allocated memory " + SIZE + r" is allocated by PyTorch"),
        "private_pools": one(r"with " + SIZE + r" allocated in private pools"),
        "unallocated": one(r"and " + SIZE + r" is reserved by PyTorch but unallocated"),
        "expandable_segments": "expandable_segments is enabled" in message,
        "other_processes": {},
    }
    for pid, number, unit in re.findall(r"Process (\d+) has " + SIZE + r" memory in use", message):
        fields["other_processes"][int(pid)] = to_bytes(number, unit)
    if fields["requested"] is None or fields["allocated"] is None:
        raise ValueError("this does not look like a PyTorch CUDA out-of-memory message")
    return fields


def diagnose(fields, card=None, growth=None, baseline=512 * 2**20, rounding=6 * 2**20):
    """Apply the decision tree. `card` is the card's capacity when it differs from the device's
    total (an emulated card); `growth` is how much PyTorch's allocated memory grew between the same
    point of two consecutive iterations, when known. `baseline` is what every process holds outside
    PyTorch anyway (its CUDA context) and what a driver keeps for itself; only memory beyond it
    counts as a cause. `rounding` absorbs the message's two-decimal rounding of every number (at
    most 5 MiB at GiB scale)."""
    req, alloc, unalloc = fields["requested"], fields["allocated"], fields["unallocated"] or 0
    reserved = alloc + unalloc
    others = sum(fields["other_processes"].values())
    this = fields["this_process"]
    non_pytorch = max(this - reserved, 0) if this is not None else None
    capacity = card or fields["total"]
    if card is None:
        # A real card: whatever the driver does not report as free, and no listed process
        # explains, is held by someone the message cannot name (a display server, another
        # container's process, or on a unified-memory GPU the operating system itself).
        unlisted = max(capacity - fields["free"] - (this or reserved) - others, 0)
        free_on_card = fields["free"]
    else:
        unlisted = 0
        free_on_card = max(capacity - (this or reserved) - others, 0)
    deficit = req - free_on_card
    numbers = {
        "requested": req, "capacity": capacity, "free_on_card": free_on_card, "deficit": deficit,
        "allocated_by_pytorch": alloc, "reserved_but_unallocated": unalloc,
        "other_processes": others, "unlisted": unlisted, "non_pytorch_in_this_process": non_pytorch,
        "growth_per_iteration": growth,
    }

    def verdict(cause, key, why, fix):
        return {"cause": cause, "discriminating_number": key, "value": numbers[key],
                "why": why, "fix": fix, "numbers": numbers}

    if growth is not None and growth > rounding:
        why = (f"PyTorch's allocated memory grows by {fmt(growth)} per iteration; "
               "something keeps every iteration's tensors alive.")
        return verdict("retained graph", "growth_per_iteration", why,
                       "run evaluation under torch.no_grad(); accumulate loss.item(), not loss")
    if unalloc + rounding >= req:
        why = (f"PyTorch already holds {fmt(unalloc)} reserved but unallocated, at least the "
               f"{fmt(req)} requested, but in pieces too small for it.")
        fix = "set PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True (or max_split_size_mb), or keep shapes stable"
        if fields["expandable_segments"]:
            why += " Expandable segments are already on, so this is residual page-level fragmentation."
            fix = "lower the peak instead: expandable segments are already on"
        return verdict("fragmentation", "reserved_but_unallocated", why, fix)
    # A holder is the cause when the part of it beyond the normal baseline would have covered the
    # shortfall. Listed processes get no allowance: on a dedicated GPU none should be there.
    holders = [("other process", "other_processes", others + unlisted, others + max(unlisted - baseline, 0)),
               ("non-PyTorch", "non_pytorch_in_this_process", non_pytorch or 0,
                max((non_pytorch or 0) - baseline, 0))]
    holders = [h for h in holders if h[3] > rounding and h[3] + rounding >= deficit]
    if holders:
        cause, key, held, _ = max(holders, key=lambda h: h[3])
        if cause == "other process":
            listed = ", ".join(f"PID {p} {fmt(b)}" for p, b in fields["other_processes"].items())
            why = (f"Other processes hold {fmt(held)} ({listed or 'none listed'}"
                   + (f"; {fmt(unlisted)} not attributed to any listed process" if unlisted > rounding else "")
                   + f"), more than the {fmt(deficit)} this request was short.")
            fix = "find the process (nvidia-smi, then ps -o pid,ppid,stat,cmd -p <pid>) and stop it"
        else:
            why = (f"This process holds {fmt(held)} outside PyTorch's allocator (its total minus "
                   f"PyTorch's {fmt(reserved)} reserved), more than the {fmt(deficit)} it was short.")
            fix = "find what allocated it (CUDA context, NCCL, another library's pool) and shrink or free it"
        return verdict(cause, key, why, fix)
    why = (f"PyTorch itself has {fmt(alloc)} allocated and nothing else explains the "
           f"{fmt(deficit)} shortfall" + (", and allocation is flat across iterations." if growth is not None
                                         else "; check growth across iterations to rule out a retained graph."))
    return verdict("capacity", "allocated_by_pytorch", why,
                   "lower the peak: smaller batch, activation checkpointing, lower precision")


def growth_from_trace(trace):
    """Growth of allocated memory between the starts of the last two iterations, the failing one
    included. The first iteration is left out: an optimizer creates its state in its first step(),
    so step 0 to step 1 grows by that state once (8 GiB for Adam here) and is not a leak."""
    points = [t["allocated"] for t in trace][1:]
    return points[-1] - points[-2] if len(points) >= 2 else None


def explain(name, result):
    n = result["numbers"]
    return "\n".join([
        f"{name}: {result['cause'].upper()}",
        f"  discriminating number: {result['discriminating_number']} = {fmt(result['value'])}",
        f"  request {fmt(n['requested'])}, short by {fmt(n['deficit'])}; reserved but unallocated "
        f"{fmt(n['reserved_but_unallocated'])}; other processes {fmt(n['other_processes'])}; "
        f"non-PyTorch {fmt(n['non_pytorch_in_this_process'])}",
        f"  why: {result['why']}",
        f"  fix: {result['fix']}",
    ])


def from_captures(path):
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    card = data["card_bytes"]
    for name, run in data["runs"].items():
        oom = run.get("oom")
        if not oom:
            continue
        trace = run.get("val_trace") or run.get("trace") or []
        result = diagnose(parse_message(oom["message"]), card=card, growth=growth_from_trace(trace))
        print(explain(name, result))
        print()


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("captures", nargs="?", help="a captures.json written by oom_lab.py")
    ap.add_argument("--message", help="the message text")
    ap.add_argument("--message-file", help="a file holding the message")
    ap.add_argument("--card", type=parse_size, help="card capacity, when the run used an emulated card")
    ap.add_argument("--growth", type=parse_size,
                    help="growth of torch.cuda.memory_allocated() between the same point of two iterations")
    ap.add_argument("--baseline", type=parse_size, default=512 * 2**20,
                    help="memory outside PyTorch that is normal, such as the CUDA context (default 512MiB)")
    ap.add_argument("--json", action="store_true", help="print the verdict as JSON")
    args = ap.parse_args()
    if args.captures:
        from_captures(args.captures)
        return
    text = args.message or (pathlib.Path(args.message_file).read_text(encoding="utf-8")
                            if args.message_file else sys.stdin.read())
    result = diagnose(parse_message(text), card=args.card, growth=args.growth, baseline=args.baseline)
    print(json.dumps(result, indent=2) if args.json else explain("message", result))


if __name__ == "__main__":
    main()
