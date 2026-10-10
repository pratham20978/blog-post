"""Read a Python wheel over HTTP without downloading it, and parse the ELF
libraries inside it.

Shared by inspect_wheel.py and resolve_stack.py. Standard library only; no GPU,
no NVIDIA driver and no CUDA Toolkit are required to run any of this.

The trick is that a wheel is a zip, and a zip's central directory sits at the
END of the file. Given an HTTP server that honours Range requests -- PyPI's
CDN does -- zipfile can seek around inside a 500 MB archive and read only the
few kilobytes it actually needs.
"""

import io
import json
import struct
import urllib.error
import urllib.request
import zipfile

USER_AGENT = "nvidia-stack-lab/1.0 (+https://canery.in)"
TIMEOUT = 90


def pypi(package, version=None):
    """Return PyPI's JSON metadata for a package, or a specific release."""
    url = f"https://pypi.org/pypi/{package}/json"
    if version:
        url = f"https://pypi.org/pypi/{package}/{version}/json"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
        return json.load(response)


def pick_wheel(release, python_tag="cp312", arch="x86_64"):
    """Pick one Linux x86_64 wheel from a release's file list.

    Order of preference: a wheel for this interpreter and architecture, then
    any Linux wheel for this architecture, then a pure-Python wheel, then
    anything. The Linux check is explicit because several projects publish a
    macosx_..._x86_64 wheel that would otherwise match on the architecture
    alone and report macOS libraries as though they were part of the stack.
    """
    wheels = [u for u in release["urls"] if u["filename"].endswith(".whl")]
    if not wheels:
        return None

    def is_linux(name):
        return "linux" in name and "macosx" not in name and "win" not in name

    for candidate in (
        [u for u in wheels if is_linux(u["filename"])
         and python_tag in u["filename"] and arch in u["filename"]],
        [u for u in wheels if is_linux(u["filename"]) and arch in u["filename"]],
        [u for u in wheels if u["filename"].endswith("-any.whl")],
    ):
        if candidate:
            return candidate[0]
    return wheels[0]


class HttpRangeFile:
    """A read-only seekable file over HTTP, backed by Range requests.

    Counts its own requests and bytes so the lab can show how little of the
    archive was actually transferred.
    """

    def __init__(self, url, size):
        self.url = url
        self.size = size
        self.pos = 0
        self.requests = 0
        self.bytes = 0

    def seek(self, offset, whence=0):
        if whence == 0:
            self.pos = offset
        elif whence == 1:
            self.pos += offset
        else:
            self.pos = self.size + offset
        return self.pos

    def tell(self):
        return self.pos

    def seekable(self):
        return True

    def readable(self):
        return True

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        if n <= 0:
            return b""
        end = min(self.pos + n, self.size) - 1
        if end < self.pos:
            return b""
        req = urllib.request.Request(
            self.url,
            headers={"User-Agent": USER_AGENT, "Range": f"bytes={self.pos}-{end}"},
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            data = response.read()
        self.requests += 1
        self.bytes += len(data)
        self.pos += len(data)
        return data


def open_wheel(url, size):
    """Return (ZipFile, HttpRangeFile) for a wheel served over HTTP."""
    handle = HttpRangeFile(url, size)
    return zipfile.ZipFile(handle), handle


def member_bytes(zf, handle, name, limit=None):
    """Decompress one member, streaming from its local header.

    `limit` caps how many uncompressed bytes to keep, so a 500 MB library can
    be sampled without pulling the whole thing.
    """
    import zlib

    info = zf.getinfo(name)
    handle.seek(info.header_offset + 26)
    name_len, extra_len = struct.unpack("<HH", handle.read(4))
    data_offset = info.header_offset + 30 + name_len + extra_len

    if info.compress_type == zipfile.ZIP_STORED:
        handle.seek(data_offset)
        return handle.read(limit or info.file_size)

    decompressor = zlib.decompressobj(-15)
    out = bytearray()
    cursor = data_offset
    stop = data_offset + info.compress_size
    while cursor < stop and (limit is None or len(out) < limit):
        handle.seek(cursor)
        chunk_end = min(cursor + (8 << 20), stop)
        chunk = handle.read(chunk_end - cursor)
        if not chunk:
            break
        out += decompressor.decompress(chunk, 0 if limit is None else limit - len(out))
        cursor = chunk_end
        if decompressor.eof:
            break
    return bytes(out)


# --- minimal ELF64 reader: just enough for the dynamic section -------------

PT_LOAD, PT_DYNAMIC = 1, 2
DT_NULL, DT_NEEDED, DT_STRTAB, DT_SONAME, DT_RPATH, DT_RUNPATH = 0, 1, 5, 14, 15, 29


class ElfTooShort(Exception):
    """The buffer does not contain the whole dynamic section."""


def elf_dynamic(buf):
    """Return {'soname', 'needed', 'rpath', 'runpath'} for an ELF64 shared object.

    Raises ElfTooShort when the dynamic section lies past the end of `buf`,
    which happens when only a prefix of a very large library was streamed.
    """
    if len(buf) < 64 or buf[:4] != b"\x7fELF":
        raise ValueError("not an ELF file")
    if buf[4] != 2:
        raise ValueError("only 64-bit ELF is supported")

    ph_off, = struct.unpack("<Q", buf[0x20:0x28])
    ph_entsize, ph_num = struct.unpack("<HH", buf[0x36:0x3A])

    loads, dynamic = [], None
    for i in range(ph_num):
        off = ph_off + i * ph_entsize
        if off + 56 > len(buf):
            raise ElfTooShort("program headers truncated")
        p_type, _flags, p_offset, p_vaddr, _paddr, p_filesz, _memsz, _align = \
            struct.unpack("<IIQQQQQQ", buf[off:off + 56])
        if p_type == PT_LOAD:
            loads.append((p_vaddr, p_offset, p_filesz))
        elif p_type == PT_DYNAMIC:
            dynamic = (p_offset, p_filesz)

    if dynamic is None:
        raise ValueError("no PT_DYNAMIC segment")
    if dynamic[0] + dynamic[1] > len(buf):
        raise ElfTooShort(
            f"dynamic section at offset {dynamic[0]:,} is past the {len(buf):,} bytes read"
        )

    def vaddr_to_offset(vaddr):
        for seg_vaddr, seg_off, seg_size in loads:
            if seg_vaddr <= vaddr < seg_vaddr + seg_size:
                return seg_off + (vaddr - seg_vaddr)
        return None

    strtab_vaddr, entries = None, []
    for off in range(dynamic[0], dynamic[0] + dynamic[1], 16):
        tag, val = struct.unpack("<qQ", buf[off:off + 16])
        if tag == DT_NULL:
            break
        if tag == DT_STRTAB:
            strtab_vaddr = val
        entries.append((tag, val))

    strtab = vaddr_to_offset(strtab_vaddr) if strtab_vaddr is not None else None
    if strtab is None or strtab >= len(buf):
        raise ElfTooShort("string table is past the bytes read")

    def string_at(index):
        start = strtab + index
        end = buf.index(b"\0", start)
        return buf[start:end].decode("utf-8", "replace")

    return {
        "soname": next((string_at(v) for t, v in entries if t == DT_SONAME), None),
        "needed": [string_at(v) for t, v in entries if t == DT_NEEDED],
        "rpath": [string_at(v) for t, v in entries if t == DT_RPATH],
        "runpath": [string_at(v) for t, v in entries if t == DT_RUNPATH],
    }


def mb(n):
    return f"{n / 1_000_000:.1f} MB"
