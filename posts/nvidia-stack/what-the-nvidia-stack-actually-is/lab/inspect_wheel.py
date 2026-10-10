#!/usr/bin/env python3
"""Read what is inside a CUDA-enabled Python wheel without installing it.

    python3 inspect_wheel.py                 # torch, latest release
    python3 inspect_wheel.py torch 2.14.0    # a specific release
    python3 inspect_wheel.py nvidia-cublas

Requires: python3 and a network connection. No GPU, no NVIDIA driver and no
CUDA Toolkit. Nothing is installed and nothing is written to disk.

It prints four things:
  1. how much of the archive had to be transferred to list all of it
  2. every shared library the wheel ships, largest first
  3. the wheel's OWN Requires-Dist, read from dist-info/METADATA
  4. for each small library, the SONAME, DT_NEEDED and DT_RPATH the dynamic
     loader will act on at import time
"""

import sys

from wheelio import (
    ElfTooShort, elf_dynamic, mb, member_bytes, open_wheel, pick_wheel, pypi,
)

# Libraries above this size are skipped: their dynamic section can sit hundreds
# of megabytes into the file, and streaming that far defeats the point.
ELF_SIZE_LIMIT = 60_000_000


def main(package="torch", version=None):
    release = pypi(package, version)
    wheel = pick_wheel(release)
    if wheel is None:
        print(f"no wheel published for {package}")
        return 1

    print(f"package        {package} {release['info']['version']}")
    print(f"wheel          {wheel['filename']}")
    print(f"download size  {mb(wheel['size'])}")

    zf, handle = open_wheel(wheel["url"], wheel["size"])
    names = zf.namelist()
    uncompressed = sum(zf.getinfo(n).file_size for n in names)
    print(f"entries        {len(names):,}")
    print(f"unpacked size  {mb(uncompressed)}")
    print(f"cost to list   {handle.requests} HTTP range requests, "
          f"{mb(handle.bytes)} transferred")

    libs = sorted(
        ((n, zf.getinfo(n).file_size) for n in names
         if n.endswith(".so") or ".so." in n),
        key=lambda pair: -pair[1],
    )
    print(f"\n--- shared libraries in the wheel ({len(libs)}) ---")
    for name, size in libs:
        print(f"  {mb(size):>10}  {name}")
    if not libs:
        print("  (none -- this wheel ships no compiled libraries)")

    meta_name = next((n for n in names if n.endswith(".dist-info/METADATA")), None)
    print(f"\n--- Requires-Dist, from {meta_name} ---")
    print("    (PyPI's JSON summary can disagree with this. The wheel is right.)")
    if meta_name:
        metadata = zf.read(meta_name).decode("utf-8", "replace")
        requires = [line for line in metadata.splitlines()
                    if line.startswith("Requires-Dist:")]
        for line in requires:
            print("   ", line.split(":", 1)[1].strip())
        if not requires:
            print("    (the wheel declares no dependencies)")

    print("\n--- what the dynamic loader will be asked for ---")
    examined = 0
    for name, size in sorted(libs, key=lambda pair: pair[1]):
        if size > ELF_SIZE_LIMIT:
            continue
        try:
            info = elf_dynamic(member_bytes(zf, handle, name, limit=size))
        except ElfTooShort as exc:
            print(f"\n  {name.split('/')[-1]}: not read -- {exc}")
            continue
        except ValueError:
            continue
        examined += 1
        print(f"\n  {name.split('/')[-1]}  (SONAME {info['soname'] or '--'})")
        for needed in info["needed"]:
            print(f"      NEEDED   {needed}")
        for entry in info["rpath"] + info["runpath"]:
            for path in entry.split(":"):
                print(f"      RPATH    {path}")

    skipped = [n for n, s in libs if s > ELF_SIZE_LIMIT]
    if skipped:
        print(f"\n  skipped {len(skipped)} library/libraries over {mb(ELF_SIZE_LIMIT)}: "
              f"{', '.join(n.split('/')[-1] for n in skipped)}")
        print("  Their dynamic section sits far into the file; reading it would mean")
        print("  streaming most of the library, which this lab deliberately does not do.")

    print(f"\ntotal transferred: {mb(handle.bytes)} over {handle.requests} requests, "
          f"examining {examined} libraries")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    sys.exit(main(args[0] if args else "torch", args[1] if len(args) > 1 else None))
