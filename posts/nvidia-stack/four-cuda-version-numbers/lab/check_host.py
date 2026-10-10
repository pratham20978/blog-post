#!/usr/bin/env python3
"""Print all four CUDA version numbers for the machine you run it on.

    python3 check_host.py

Requires: python3 only. No GPU and no NVIDIA driver are needed -- on a machine
without them the script says so for each number rather than failing, which is
itself the useful output: it shows which of the four numbers are properties of
the host and which travel with your packages.

Each number is read from the artifact that owns it, never from another
command's opinion of it:

  1. kernel-mode driver  /proc/driver/nvidia/version, written by nvidia.ko
  2. CUDA driver ceiling cuDriverGetVersion(), called in libcuda.so.1 itself
  3. CUDA runtime        cudaRuntimeGetVersion(), called in the libcudart your
                         environment would actually load
  4. Toolkit compiler    nvcc --version, if a Toolkit is on PATH at all

Nothing here parses nvidia-smi's text output. nvidia-smi is a reader of the
same driver, not the source of any of these numbers.
"""

import ctypes
import ctypes.util
import glob
import os
import re
import shutil
import subprocess
import sys
import sysconfig

# CUDA's own encoding: 1000 * major + 10 * minor.
DECODE = lambda v: f"{v // 1000}.{(v % 1000) // 10}"

# Minimum driver branch per major family, from NVIDIA's CUDA Compatibility
# documentation. Only the major family matters -- that is the whole point of
# minor version compatibility.
MINIMUM_DRIVER = {11: 450, 12: 525, 13: 580}


def rule(title):
    print(f"\n--- {title} " + "-" * max(0, 58 - len(title)))


def kernel_mode_driver():
    """Number 1. The loaded kernel module, straight from procfs."""
    path = "/proc/driver/nvidia/version"
    if not os.path.exists(path):
        return None, f"{path} is absent -- no NVIDIA kernel module is loaded"
    with open(path) as handle:
        text = handle.read().strip()
    m = re.search(r"Kernel Module\s+([\d.]+)", text)
    return (m.group(1) if m else None), text


def cuda_driver_ceiling():
    """Number 2. Ask libcuda.so.1 directly what it will serve."""
    soname = "libcuda.so.1"
    try:
        lib = ctypes.CDLL(soname)
    except OSError as exc:
        return None, f"{soname} could not be loaded -- {exc}"
    version = ctypes.c_int(0)
    # cuDriverGetVersion needs no context and does not initialise CUDA.
    status = lib.cuDriverGetVersion(ctypes.byref(version))
    if status != 0:
        return None, f"cuDriverGetVersion returned CUDA error {status}"
    return version.value, f"{soname} -> cuDriverGetVersion = {version.value}"


def cuda_runtime():
    """Number 3. The libcudart this environment would load, asked directly."""
    candidates = []
    for base in {sysconfig.get_paths()["purelib"], sysconfig.get_paths()["platlib"]}:
        candidates += sorted(glob.glob(os.path.join(base, "nvidia", "**", "libcudart.so*"),
                                       recursive=True))
    found = ctypes.util.find_library("cudart")
    if found:
        candidates.append(found)

    if not candidates:
        return None, None, ("no libcudart found in site-packages or on the loader path "
                            "-- nothing in this environment carries a CUDA runtime")
    path = candidates[0]
    try:
        lib = ctypes.CDLL(path)
    except OSError as exc:
        return None, path, f"{path} could not be loaded -- {exc}"
    version = ctypes.c_int(0)
    # Since CUDA 12.0 this call does not initialise CUDA; it returns a
    # compile-time constant, so it works with no driver present.
    status = lib.cudaRuntimeGetVersion(ctypes.byref(version))
    if status != 0:
        return None, path, f"cudaRuntimeGetVersion returned CUDA error {status}"
    return version.value, path, None


def toolkit():
    """Number 4. Whatever nvcc happens to be on PATH, if any."""
    exe = shutil.which("nvcc")
    if not exe:
        return None, None, "no nvcc on PATH -- no CUDA Toolkit compiler is installed"
    try:
        out = subprocess.run([exe, "--version"], capture_output=True, text=True,
                             timeout=30).stdout
    except (OSError, subprocess.SubprocessError) as exc:
        return None, exe, f"nvcc could not be run -- {exc}"
    m = re.search(r"release\s+([\d.]+)", out)
    return (m.group(1) if m else None), exe, None


def main():
    print("Four CUDA version numbers, each read from the artifact that owns it.")
    print(f"python    {sys.version.split()[0]}")

    rule("1. kernel-mode driver (the KMD, nvidia.ko)")
    kmd, kmd_detail = kernel_mode_driver()
    print(f"    {kmd_detail}")
    print(f"    => KMD version: {kmd or 'not present'}")

    rule("2. CUDA driver ceiling (the UMD, libcuda.so.1)")
    umd, umd_detail = cuda_driver_ceiling()
    print(f"    {umd_detail}")
    print(f"    => highest CUDA this driver will serve: "
          f"{DECODE(umd) if umd else 'not present'}")

    rule("3. CUDA runtime in this environment (libcudart)")
    rt, rt_path, rt_error = cuda_runtime()
    if rt_path:
        print(f"    {rt_path}")
    if rt_error:
        print(f"    {rt_error}")
    if rt:
        print(f"    cudaRuntimeGetVersion = {rt}")
    print(f"    => runtime your binaries were built against: "
          f"{DECODE(rt) if rt else 'none in this environment'}")

    rule("4. Toolkit compiler (nvcc on PATH)")
    tk, tk_path, tk_error = toolkit()
    if tk_path:
        print(f"    {tk_path}")
    if tk_error:
        print(f"    {tk_error}")
    print(f"    => nvcc release: {tk or 'not installed'}")

    rule("the only comparison that decides whether a launch works")
    if rt is None:
        print("    No CUDA runtime in this environment, so there is nothing to check.")
    elif umd is None:
        print(f"    This environment carries CUDA {DECODE(rt)}, and no CUDA driver is")
        print("    present to serve it. Every CUDA call would fail at initialisation.")
        major = rt // 1000
        floor = MINIMUM_DRIVER.get(major)
        if floor:
            print(f"    A CUDA {major}.x runtime needs a driver of branch {floor} or newer.")
    else:
        verdict = "runs" if rt <= umd else "FAILS"
        print(f"    runtime {DECODE(rt)} vs driver ceiling {DECODE(umd)}  ->  {verdict}")
        if rt // 1000 != umd // 1000:
            print("    Different major families: minor version compatibility does not")
            print("    apply, and only the forward-compatibility package could bridge it.")
    print("\n    Note that number 4 played no part in that comparison. nvcc decides")
    print("    what gets built, never what gets loaded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
