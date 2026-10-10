#!/usr/bin/env python3
"""Read a framework's CUDA version numbers out of its wheels, without installing.

    python3 cuda_versions.py                  # torch, latest release
    python3 cuda_versions.py torch 2.14.0     # a specific release

Requires: python3 and a network connection. No GPU, no NVIDIA driver, no CUDA
Toolkit. Nothing is installed. The last step writes one extracted library into
a temporary directory so it can be loaded and asked its own version; delete
that directory afterwards if you like, nothing else on disk is touched.

Three of the four version numbers in the article are properties of artifacts
rather than of a running machine, so all three can be read ahead of time:

  * the build-time CUDA the framework recorded, from `torch/version.py`
  * the CUDA runtime it will actually load, from the pinned component wheel
  * CUDART_VERSION and CUDA_VERSION, from the headers inside that wheel

The fourth -- the driver's CUDA ceiling -- belongs to the host and cannot be
read from a package index. That is what check_host.py is for, and the gap
between the two scripts is the point the article makes.
"""

import ctypes
import os
import re
import sys
import tempfile

from wheelio import member_bytes, mb, open_wheel, pick_wheel, pypi

# NVIDIA's own encoding, documented on cudaDriverGetVersion and
# cudaRuntimeGetVersion in cuda_runtime_api.h.
def decode(version_int):
    """1000 * major + 10 * minor, back into a dotted string."""
    return f"{version_int // 1000}.{(version_int % 1000) // 10}"


def read_member(zf, handle, suffix):
    """Return the text of the first member whose name ends with `suffix`."""
    for name in zf.namelist():
        if name.endswith(suffix):
            return name, zf.read(name).decode("utf-8", "replace")
    return None, None


def find_pin(requires, package):
    """Pull one pinned requirement out of a requires_dist list."""
    for line in requires or []:
        head = line.split(";")[0].strip()
        if re.match(rf"^{re.escape(package)}\b", head):
            return head
    return None


def ask_the_runtime(zf, handle, member):
    """Extract libcudart, load it, and call cudaRuntimeGetVersion for real.

    This is the claim worth testing rather than reading: since CUDA 12.0 the
    call returns a compile-time constant and no longer initialises CUDA, so it
    must answer on a machine with no GPU and no driver at all. If that were
    wrong, this is where it would fail.
    """
    blob = member_bytes(zf, handle, member, limit=zf.getinfo(member).file_size)
    directory = tempfile.mkdtemp(prefix="cudart-")
    path = os.path.join(directory, member.split("/")[-1])
    with open(path, "wb") as out:
        out.write(blob)
    try:
        lib = ctypes.CDLL(path)
    except OSError as exc:
        return None, f"could not load it here -- {exc}"
    value = ctypes.c_int(0)
    status = lib.cudaRuntimeGetVersion(ctypes.byref(value))
    if status != 0:
        return None, f"cudaRuntimeGetVersion returned CUDA error {status}"
    return value.value, path


def main(package="torch", version=None):
    release = pypi(package, version)
    info = release["info"]
    wheel = pick_wheel(release)
    if wheel is None:
        print(f"no Linux wheel published for {package}")
        return 1

    print(f"=== {package} {info['version']} " + "=" * 30)
    print(f"wheel            {wheel['filename']}")
    print(f"index version    {info['version']}   <- what pip resolved")

    zf, handle = open_wheel(wheel["url"], wheel["size"])

    # 1. What the framework recorded about its own build.
    name, text = read_member(zf, handle, f"{package}/version.py")
    build_cuda = None
    if text:
        print(f"\n--- {name} ---")
        for line in text.splitlines():
            if re.match(r"^\s*(__version__|cuda|hip|rocm|xpu|git_version)\b", line):
                print("   ", line.strip())
        m = re.search(r"^\s*cuda[^=]*=\s*'([^']+)'", text, re.M)
        build_cuda = m.group(1) if m else None
        m = re.search(r"^__version__\s*=\s*'([^']+)'", text, re.M)
        if m and "+" in m.group(1):
            local = m.group(1).split("+", 1)[1]
            print(f"\n    note: the local label '+{local}' is not part of the version pip")
            print(f"          resolved. PyPI published this as {info['version']}.")
    else:
        print(f"\n    ({package} ships no version.py; build-time CUDA not recorded there)")

    # 2. Which runtime the dependency chain actually pins.
    print("\n--- the pin chain ---")
    toolkit_pin = find_pin(info.get("requires_dist"), "cuda-toolkit")
    runtime_pin = find_pin(info.get("requires_dist"), "nvidia-cuda-runtime")
    print(f"    {package} declares      {toolkit_pin or runtime_pin or '(no CUDA pin found)'}")

    runtime_version = None
    runtime_cuda = None
    if toolkit_pin and not runtime_pin:
        pinned = re.search(r"==\s*([\d.]+)", toolkit_pin)
        if pinned:
            tk = pypi("cuda-toolkit", pinned.group(1))
            inner = find_pin(tk["info"].get("requires_dist"), "nvidia-cuda-runtime")
            print(f"    cuda-toolkit pins    {inner}")
            m = re.search(r"==\s*([\d.]+)", inner or "")
            runtime_version = m.group(1).rstrip(".") if m else None
    elif runtime_pin:
        m = re.search(r"==\s*([\d.]+)", runtime_pin)
        runtime_version = m.group(1).rstrip(".") if m else None

    # 3. The version macros, read from the headers in that exact wheel.
    if runtime_version:
        rt = pypi("nvidia-cuda-runtime", runtime_version)
        rt_wheel = pick_wheel(rt)
        rzf, rhandle = open_wheel(rt_wheel["url"], rt_wheel["size"])
        print(f"\n--- headers inside {rt_wheel['filename']} ---")
        for header, macro in (("cuda_runtime_api.h", "CUDART_VERSION"),
                              ("include/cuda.h", "CUDA_VERSION")):
            hname, htext = read_member(rzf, rhandle, header)
            found = re.search(rf"#define\s+{macro}\s+(\d+)", htext or "")
            if found:
                raw = int(found.group(1))
                if macro == "CUDART_VERSION":
                    runtime_cuda = raw
                print(f"    {macro:16s} {raw}   -> CUDA {decode(raw)}"
                      f"   ({hname.split('/')[-1]})")
        libs = [n for n in rzf.namelist() if ".so" in n]
        for lib in libs:
            print(f"    ships            {lib.split('/')[-1]}")

        if libs:
            print("\n--- asking that runtime directly, with no driver present ---")
            reported, detail = ask_the_runtime(rzf, rhandle, libs[0])
            if reported is None:
                print(f"    {detail}")
            else:
                print(f"    loaded           {detail}")
                print(f"    cudaRuntimeGetVersion() = {reported}   -> CUDA "
                      f"{decode(reported)}")
                print("    It answered without a GPU, a driver, or a CUDA context,")
                print("    because since CUDA 12.0 the value is a compile-time constant.")
        print(f"\n    transferred      {mb(rhandle.bytes)} in {rhandle.requests} requests")

    print("\n--- what this tells you, and what it cannot ---")
    print(f"    build-time CUDA  {build_cuda or '(not recorded)'}"
          "        <- number 4, as the framework recorded it")
    print(f"    runtime it loads {decode(runtime_cuda) if runtime_cuda else '(not resolved)'}"
          "        <- number 3, a constant in the binary")
    print("    driver ceiling   unknown from here"
          "  <- number 2, a property of the host")
    print("    kernel driver    unknown from here"
          "  <- number 1, a property of the host")
    print("\n    Run check_host.py on the target machine for the other two.")
    print(f"\ntotal transferred: {mb(handle.bytes)} over {handle.requests} requests")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    sys.exit(main(args[0] if args else "torch", args[1] if len(args) > 1 else None))
