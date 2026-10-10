#!/usr/bin/env python3
"""Answer one question: when PyTorch asks the loader for libcublas.so.13, who
is supposed to provide it?

    python3 resolve_stack.py           # torch, latest release
    python3 resolve_stack.py torch 2.14.0

Requires: python3 and a network connection. No GPU, no NVIDIA driver and no
CUDA Toolkit. Nothing is installed.

It walks the dependency graph declared by the wheel itself, lists the shared
libraries every wheel in that graph ships, then matches those against the
DT_NEEDED entries of the root package's own libraries. Anything left over is
either part of the base system or has to come from the host NVIDIA driver --
and telling those two apart is the point of the exercise.
"""

import re
import sys

from wheelio import (
    ElfTooShort, elf_dynamic, mb, member_bytes, open_wheel, pick_wheel, pypi,
)

ELF_SIZE_LIMIT = 60_000_000
MAX_PACKAGES = 40

# Present in any glibc userland; never shipped by a Python wheel.
SYSTEM_LIBS = re.compile(
    r"^(ld-linux.*|libc|libm|libdl|libpthread|librt|libutil|libstdc\+\+|libgcc_s"
    r"|libgomp|libatomic|libcrypt|libnsl|libresolv)\.so"
)
# Shipped by the NVIDIA display driver, never by a wheel.
DRIVER_LIBS = re.compile(r"^(libcuda\.so|libnvidia-.*\.so|libnvcuvid\.so)")

REQUIREMENT = re.compile(
    r"^\s*(?P<name>[A-Za-z0-9._-]+)\s*"
    r"(?:\[(?P<extras>[^\]]*)\])?\s*"
    r"(?P<spec>[^;]*)"
    r"(?:;\s*(?P<marker>.*))?$"
)


def marker_allows(marker, active_extras):
    """Evaluate the small subset of PEP 508 markers these packages actually use.

    Assumes a Linux x86_64 CPython target. Unknown markers are allowed through
    rather than silently dropped, so the output errs toward showing too much.
    """
    if not marker:
        return True
    text = marker.strip()

    extras_named = set(re.findall(r'extra\s*==\s*[\'"]([^\'"]+)[\'"]', text))
    if extras_named and not (extras_named & active_extras):
        return False

    for var, ours in (("platform_system", "Linux"),
                      ("sys_platform", "linux"),
                      ("platform_machine", "x86_64")):
        equals = set(re.findall(rf'{var}\s*==\s*[\'"]([^\'"]+)[\'"]', text))
        if equals and ours not in equals:
            return False
        if re.search(rf'{var}\s*!=\s*[\'"]{re.escape(ours)}[\'"]', text):
            return False
    return True


def requirements(metadata, active_extras):
    """Yield (name, extras) for each Requires-Dist line that applies to us."""
    for line in metadata.splitlines():
        if not line.startswith("Requires-Dist:"):
            continue
        match = REQUIREMENT.match(line.split(":", 1)[1].strip())
        if not match:
            continue
        if not marker_allows(match.group("marker"), active_extras):
            continue
        extras = {e.strip() for e in (match.group("extras") or "").split(",") if e.strip()}
        yield match.group("name"), extras


def wheel_facts(package, version=None):
    """Return (metadata_text, {soname: size}, small_library_dynamic_info)."""
    release = pypi(package, version)
    wheel = pick_wheel(release)
    if wheel is None:
        return release["info"]["version"], "", {}, {}

    zf, handle = open_wheel(wheel["url"], wheel["size"])
    names = zf.namelist()

    provided = {
        n.split("/")[-1]: zf.getinfo(n).file_size
        for n in names if n.endswith(".so") or ".so." in n
    }

    meta_name = next((n for n in names if n.endswith(".dist-info/METADATA")), None)
    metadata = zf.read(meta_name).decode("utf-8", "replace") if meta_name else ""

    dynamic = {}
    for name in names:
        if not (name.endswith(".so") or ".so." in name):
            continue
        size = zf.getinfo(name).file_size
        if size > ELF_SIZE_LIMIT:
            dynamic[name.split("/")[-1]] = None      # too big to read cheaply
            continue
        try:
            dynamic[name.split("/")[-1]] = elf_dynamic(
                member_bytes(zf, handle, name, limit=size))
        except (ElfTooShort, ValueError):
            dynamic[name.split("/")[-1]] = None

    return release["info"]["version"], metadata, provided, dynamic


def main(root="torch", version=None):
    print(f"resolving the declared dependency graph of {root}\n")

    root_version, metadata, root_provides, root_dynamic = wheel_facts(root, version)
    print(f"{root}=={root_version} ships {len(root_provides)} shared libraries")

    providers = {name: root for name in root_provides}
    footprint = dict(root_provides)
    queue, seen = [], {root}
    for name, extras in requirements(metadata, set()):
        queue.append((name, extras))

    print("\n--- walking the graph ---")
    print(f"  {root} requires: " + ", ".join(
        n + (f"[{','.join(sorted(e))}]" if e else "") for n, e in queue))

    while queue and len(seen) < MAX_PACKAGES:
        name, extras = queue.pop(0)
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        try:
            version_, meta, provides, _ = wheel_facts(name)
        except Exception as exc:                      # a pure-Python or absent wheel
            print(f"  {name}: skipped ({type(exc).__name__})")
            continue
        if provides:
            print(f"  {name}=={version_} provides {len(provides)} libraries, "
                  f"{mb(sum(provides.values()))}")
            for lib, size in sorted(provides.items(), key=lambda kv: -kv[1])[:4]:
                print(f"      {mb(size):>10}  {lib}")
            if len(provides) > 4:
                print(f"      ... and {len(provides) - 4} more")
        for lib, size in provides.items():
            providers.setdefault(lib, name)
            footprint[lib] = max(footprint.get(lib, 0), size)
        for dep_name, dep_extras in requirements(meta, extras):
            if dep_name.lower() not in seen:
                queue.append((dep_name, dep_extras))

    needed = {}
    for lib, info in root_dynamic.items():
        if info:
            for dependency in info["needed"]:
                needed.setdefault(dependency, []).append(lib)

    print(f"\n--- every library {root}'s own binaries ask the loader for ---\n")
    print(f"  {'library':<26} {'provided by':<34} asked for by")
    print(f"  {'-' * 26} {'-' * 34} {'-' * 28}")
    unresolved = []
    for dependency in sorted(needed):
        askers = ", ".join(sorted(needed[dependency])[:2])
        if len(needed[dependency]) > 2:
            askers += f" +{len(needed[dependency]) - 2}"
        if dependency in providers:
            source = f"wheel: {providers[dependency]}"
        elif DRIVER_LIBS.match(dependency):
            source = "*** THE HOST NVIDIA DRIVER ***"
            unresolved.append(dependency)
        elif SYSTEM_LIBS.match(dependency):
            source = "the base system (glibc, libstdc++)"
        else:
            source = "not found in this graph"
            unresolved.append(dependency)
        print(f"  {dependency:<26} {source:<34} {askers}")

    unread = [k for k, v in root_dynamic.items() if v is None]
    if unread:
        print(f"\n  not read (larger than {mb(ELF_SIZE_LIMIT)}): {', '.join(sorted(unread))}")
        print("  Their DT_NEEDED lists are not included above.")

    print(f"\n--- what that adds up to ---")
    print(f"  {len(seen)} packages in the resolved graph")
    print(f"  {len(footprint)} shared libraries")
    print(f"  {sum(footprint.values()) / 1_000_000_000:.2f} GB of compiled code, unpacked")
    print("  and not one byte of it is the thing that talks to the GPU.")

    print("\n--- the point ---")
    for dependency in unresolved:
        if DRIVER_LIBS.match(dependency):
            print(f"  {dependency} is named by the binaries and shipped by no wheel in the")
            print("  graph. It comes from the NVIDIA driver installed on the host, and that")
            print("  is the one layer pip can never deliver.")
    if not unresolved:
        print("  Every requested library was found inside the wheel graph.")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    sys.exit(main(args[0] if args else "torch", args[1] if len(args) > 1 else None))
