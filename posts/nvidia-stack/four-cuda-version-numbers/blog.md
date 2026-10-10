---
title: "The Four CUDA Version Numbers"
slug: "four-cuda-version-numbers"
date: 2026-09-23
updated: 2026-09-23
summary: "nvidia-smi prints a CUDA version you never installed: a ceiling, not an inventory. Only two of the four numbers on a machine decide whether your code runs."
tags: [machine-learning, cuda, nvidia, gpu, versioning, compatibility]
category: "machine-learning"
series: nvidia-stack
series_position: 2
tier: L2
difficulty: intermediate
prerequisites: ["python", "linux-shell", "the NVIDIA layer map"]
reading_minutes: 20
cover_image: "https://minio.canery.in/media/cover-four-cuda-version-numbers.png"
canonical_url: "https://canery.in/blogs/four-cuda-version-numbers"
---
> [!NOTE]
> **Insights** — The CUDA version `nvidia-smi` prints is a *ceiling*: the newest CUDA your installed driver is willing to serve. It is not an inventory of what is installed, and NVIDIA renamed the field to `CUDA UMD Version` to say so. Four different numbers on one machine are all correctly called "the CUDA version", and only the relationship between two of them decides whether your program runs. The compiler version — the one most people check first — takes no part in that decision at all.

**Level:** intermediate · **You need:** Python, a shell, and [part 1&#39;s layer map](https://canery.in/blogs/what-the-nvidia-stack-actually-is#the-problem-five-different-things-are-called-cuda) · **Time:** ~20 min

> [!TIP]
> **Runnable lab, no GPU required.** Two of these four numbers live in files you can read before installing anything, and a third answers on a machine with no driver at all. Every artifact-side number below was produced on a laptop with no NVIDIA GPU. The scripts are under [Lab downloads](#lab-downloads).

## Why this matters

A colleague reports that the training job will not start. You ask what CUDA they have. They run `nvidia-smi`, which says 13.0. You run `nvcc --version` on the same box, which says 13.4. Python says `torch.version.cuda` is `'13.0'`. Three answers, one machine, and every one of them is correct.

Now the real question arrives: will this wheel run on this driver? Nothing you have printed so far answers it, because none of those commands reported the two numbers the answer depends on. Most of the time you guess, upgrade the driver, and the problem goes away — which teaches the wrong lesson, because next time the driver is frozen by a platform team and guessing is not available.

Part 1 of this series established *which artifact* owns each layer of the stack. This part is about *what each artifact's version number promises*, which is a different question with a much sharper answer.

## The problem: four numbers, one word

Say "CUDA 13" on a machine and you have named four separately versioned things. Here they are with the artifact each one is a property of.

![Four rows: kernel module, libcuda.so.1, libcudart.so.13 and nvcc, each with the file on disk, the command that prints its version, and what that version promises](https://minio.canery.in/media/fig-01-four-numbers-four-cuda-version-numbers.png)

*Figure 1. The fourth column is the one that matters: two of these numbers are facts about your host, one is a constant baked into your binaries, and one describes a compiler that may not even be installed.*

**The kernel-mode driver.** The loaded `nvidia.ko` module — the only code here that talks to the hardware. Its version looks like `580.65.06`, a driver branch number with no CUDA in it at all.  NVIDIA's own tooling calls this the KMD version, and `nvidia-smi`'s older `Driver Version` field is now deprecated in its favour.

**The CUDA user-mode driver.** `libcuda.so.1`, the shared library that implements the driver API every CUDA program eventually calls. It is installed by the driver package, never by a wheel. NVIDIA defines the number it reports as the newest CUDA release the driver is able to support, and their documentation adds that this is "usually, but not always" the version of the Toolkit installed on the system.  This is the number `nvidia-smi` prints, and the field is now called `CUDA UMD Version` because the old name `CUDA Version` implied an inventory it never was.  NVIDIA describes the rename as making the fields reflect the source of the version information more accurately.

**The CUDA runtime.** `libcudart.so.13`, which arrives inside Python wheels and is what your framework was compiled against. Its version is not discovered at run time. It is a constant compiled into the library.

**The Toolkit compiler.** `nvcc`, plus the headers and the developer libraries that ship with it. A machine can have a driver and no Toolkit, or a Toolkit and no driver, and both situations are ordinary.

Terminology for the rest of this post: *KMD* is the kernel-mode driver, *UMD* is the user-mode driver `libcuda.so.1`, *the runtime* is `libcudart`, and *the Toolkit* is whatever `nvcc` belongs to. Those four words replace the single overloaded word "CUDA", and once they are separate the compatibility rules stop being arbitrary.

## Worked example: five commands, four numbers

Take the machine NVIDIA uses in its own compatibility documentation: a Tesla T4 with driver 580.65.06 installed, running an application built with the CUDA 13.4 Toolkit.  Five commands, and watch where each answer comes from.

**Command 1 — `nvidia-smi`.** The header prints `580.65.06` as the driver version and `13.0` as the CUDA version.  Two numbers from one command, and they come from two different artifacts: `580.65.06` is the kernel module, `13.0` is the ceiling the user-mode driver advertises.

**Command 2 — `cat /proc/driver/nvidia/version`.** Procfs, written by the kernel module itself. This is the KMD number without an intermediary, and it is the one to trust when you want to know what is actually loaded rather than what a tool reports.

**Command 3 — the application's own `deviceQuery`.** On that machine it prints `CUDA Driver Version / Runtime Version 13.0 / 13.4`, and the run passes.  The driver side of that pair is the same `13.0` from `nvidia-smi`. The runtime side, `13.4`, is the Toolkit the binary was compiled with — a *newer* number than the driver reports, and the program runs anyway. That is the whole subject of this post in one line.

**Command 4 — `python -c "import torch; print(torch.version.cuda)"`.** On a `torch` 2.14.0 install this prints `13.0`, because `torch/version.py` records `cuda = '13.0'`.  Follow the dependency chain and the same number shows up as an artifact: `torch` 2.14.0 declares `cuda-toolkit[…]==13.0.3` on Linux,  that release pins `nvidia-cuda-runtime==13.0.96.*`,  and the headers inside *that* wheel define `CUDART_VERSION` as `13000`.

**Command 5 — `nvcc --version`.** Whatever Toolkit is on `PATH`, which on a wheel-only install is nothing at all. No `nvcc`, no error, and the job still trains.

![A matrix of five commands against four artifacts, with a filled dot where a command reports that artifact’s version, and two dots in the kernel-module column](https://minio.canery.in/media/fig-02-five-commands-four-cuda-version-numbers.png)

*Figure 2. Read down the first column: two different commands land on the kernel module, which is why the title says four numbers and not five.*

Figure 2 shows the convergence that makes the count work. Five commands yield six readouts — `nvidia-smi` alone prints two — but its driver field and procfs are reading the same kernel module, so four distinct numbers sit underneath. Each of the four has exactly one artifact that owns it, and asking any other artifact is hearsay.

Notice what did not happen anywhere in that list. No command consulted a registry, a manifest or a central version. The runtime never asked the driver what version to be, and the driver never asked the Toolkit. Each number was decided when its artifact was built, and the only thing that happens at run time is a comparison.

## Intuition: a ceiling, a constant, and a compiler

Three of these numbers behave in completely different ways, and mixing them up is the entire failure mode.

**The driver's number is a ceiling.** `cudaDriverGetVersion` is documented as returning *the latest version of CUDA supported by the driver*, and it returns `0` when no driver is installed.  A ceiling is not a statement about what exists on the machine; it is a statement about the highest thing that would be accepted. A driver reporting 13.0 has not installed CUDA 13.0 anywhere. It has promised to serve requests up to that level.

**The runtime's number is a constant.** Since CUDA 12.0, `cudaRuntimeGetVersion` no longer initialises CUDA; NVIDIA states that its sole purpose is to return a compile-time constant naming the Toolkit version.  That is a strong claim, so the lab tests it rather than quoting it: extract `libcudart.so.13` from the wheel, load it with `ctypes`, and call the function on a machine with no GPU and no driver. It returns `13000`.  The number was decided by whoever compiled that library and has been inert ever since.

**The compiler's number is neither.** `nvcc --version` tells you which compiler is installed. It has no bearing on what a pre-built wheel does, because that wheel was compiled somewhere else, months ago, by a different `nvcc`.

![A vertical version axis with the driver ceiling drawn as a line and three application runtimes positioned below, at, and above it](https://minio.canery.in/media/fig-03-ceiling-and-constant-four-cuda-version-numbers.png)

*Figure 3. The failing case is the one on the left, below the ceiling — not the one on the right, above it. Distance from the ceiling is not what is being tested; the major family is.*

Figure 3 is the mental model worth keeping: a fixed ceiling set by the host, and constants carried in by whatever you installed. Nothing negotiates. There is no handshake in which the runtime asks for a downgrade, and no mechanism by which a wheel adapts to an older driver. There is a comparison, and then either the program runs or CUDA fails to initialise.

The analogy that helps here is a building's freight-lift weight limit, and it breaks in a specific place worth naming. The limit is posted, fixed, and checked once at the door — that much transfers. What does not transfer is that a lift refuses a heavy load gracefully and tells you why, whereas CUDA's check happens at initialisation — so a binary the driver cannot serve fails on its first device call, with an error that names nothing about versions at all.

## What does minor version compatibility actually promise?

The promise is narrow and precise, and it is worth stating exactly because almost every summary of it overreaches.

From CUDA 11 onward, an application compiled with **any** Toolkit release inside a major family runs — with a limited feature set — on any system whose driver meets that family's minimum.  The minimum is per *family*, not per release, and NVIDIA is explicit that it may differ from the driver packaged with the Toolkit while still belonging to the same major release.

![A driver-number axis from 450 to 615 with three bands drawn to scale: CUDA 11.x from 450, 12.x from 525, 13.x from 580](https://minio.canery.in/media/fig-04-driver-floors-four-cuda-version-numbers.png)

*Figure 4. Notice the bands overlap nothing: each major family starts exactly where the previous one's window closes, so a single driver number places you in exactly one of them.*

Figure 4 gives the whole table: CUDA 13.x needs driver 580 or newer, CUDA 12.x needs 525 or newer, and CUDA 11.x needs 450 or newer.  That is three numbers to remember instead of a release-by-release matrix, and it is why the T4 example above works: the application is CUDA 13.4, the driver is 580.65.06, and 580 clears the 13.x floor.

This replaced a genuinely worse arrangement. Before CUDA 11.0 the minimum driver for a Toolkit was simply the driver shipped with it, so every minor Toolkit bump forced a driver upgrade on every machine.  The mechanism that changed it — NVIDIA calls it CUDA Enhanced Compatibility — arrived in CUDA 11.1 and works by relaxing the runtime's own minimum-driver check.  Underneath it sits a versioning commitment: from CUDA 11 the Toolkit follows an X.Y.Z scheme in which a major change breaks binary compatibility and a minor change maintains it.

Running the other way, the guarantee is older and stronger. The driver API has a versioned C-style ABI — an application binary interface, the byte-level contract a compiled program relies on — so it is binary compatible across driver versions even though it is not source compatible across SDK releases.  In practice that means an application compiled with a Toolkit as old as CUDA 3.2 still runs on a modern driver.  Upgrading a driver is therefore safe for existing binaries; it is *downgrading* a Toolkit expectation onto an old driver that needs a rule.

### The three caveats, and what each one costs

NVIDIA documents exactly three limits on that promise.  They are not footnotes; each one turns the guarantee off for a whole class of program.

![Three caveats as boxes — features spanning toolkit and driver, PTX compilation, and the target architecture flag — each with the error code it produces](https://minio.canery.in/media/fig-05-three-caveats-four-cuda-version-numbers.png)

*Figure 5. Only the left card carries a runtime error code. The other two fail at build time or simply do not launch, which is why they are the ones that surprise people.*

**Features that span the Toolkit and the driver.** Some new capabilities need code on both sides. An application that uses one on an older driver gets `cudaErrorCallRequiresNewerDriver` — value 36 in the shipped headers.   NVIDIA's advice is to check for the feature explicitly rather than assume it, which is the right shape of advice and the one nobody follows.

**Applications that compile device code to PTX.** PTX — Parallel Thread Execution — is NVIDIA's virtual instruction set: a portable intermediate form that the driver compiles into real machine code on the target GPU. Ship PTX and these guarantees do not apply on older drivers, full stop.  The reason is that the driver *is* the compiler for it, so shipping PTX quietly makes the driver part of your build toolchain.

**Passing a target architecture to `nvcc`.** Minor version compatibility requires it.  That flag is where *version* compatibility ends and *architecture* compatibility begins, and this series deliberately splits them: part 6 owns compute capability, fatbinaries and what `-arch` actually selects. The only thing to carry forward is that the two axes are independent, and satisfying one says nothing about the other.

If any caveat bites, the repair is the same as it was before CUDA 11: install a driver from the same minor version as the Toolkit you built with, or newer.

## What does forward compatibility actually require?

Minor version compatibility works inside one major family. Cross a major boundary — a CUDA 13 application on a driver from the 12 series — and it does not apply. The forward-compatibility package exists for exactly that case, and it is surrounded by preconditions that get dropped from every summary.

The mechanism first, and it has been available since CUDA 10.  NVIDIA's own sentence is the one to keep: forward compatibility is defined between the **kernel driver and the CUDA driver**, whereas minor version compatibility is defined between the **CUDA runtime and the CUDA driver**.  The two mechanisms span different gaps in the same stack.

![The stack with two brackets: minor version compatibility spanning runtime to user-mode driver, forward compatibility spanning user-mode driver to kernel module](https://minio.canery.in/media/fig-06-two-boundaries-four-cuda-version-numbers.png)

*Figure 6. The two brackets share exactly one box — `libcuda.so.1`. Every compatibility question in this post is really a question about which side of that library you are standing on.*

Figure 6 explains both the appeal and the limits. The package — named `cuda-compat-<major>-<minor>`, installed into `/usr/local/cuda-<version>/compat`  — ships a newer `libcuda.so` alongside the debugger, JIT and PTX compiler libraries, with two more components added at CUDA 13.4.  It does not touch `nvidia.ko`. For a datacenter where the kernel driver is under change control and the application team wants a newer CUDA, that is the entire value proposition.

Now the preconditions.

**It only works on some hardware.** NVIDIA supports forward compatibility on data center GPUs, select NGC Server Ready SKUs of RTX cards, and Jetson boards.  An ordinary consumer card is not on that list. This is the precondition most often missed, and it means the package is not a general answer to "my driver is too old" — it is a datacenter answer.

**Installing it does nothing on its own.** NVIDIA notes that the package provides the libraries and does not configure the system to find them; setting `LD_LIBRARY_PATH` to the `compat` directory is the documented step.  Skip it and the loader keeps resolving `libcuda.so.1` to the old host driver, silently, with no error to explain why nothing changed.

**It expires in both directions.** Each package is built from the driver libraries matching the CUDA release it supports — `cuda-compat-13-4` from driver version 615, for instance  — and an older package is not supported on a newer driver.  That is why a full system upgrade has to remove it rather than leave it in place. The pairing is what NVIDIA's support matrix encodes: driver 535 with CUDA 12.2, 570 with 12.8, 580 with 13.0, and on up to 615 with 13.4.

**Some features never come back.** CUDA–OpenGL and CUDA–Vulkan interop do not work under any forward-compatibility package, in any major family.  If your workload needs graphics interop, this path is closed regardless of hardware.

Two error codes tell you the check failed rather than the application: `CUDA_ERROR_SYSTEM_DRIVER_MISMATCH` (803) when the display driver and CUDA driver versions disagree, and `CUDA_ERROR_COMPAT_NOT_SUPPORTED_ON_DEVICE` (804) when the system was upgraded for forward compatibility but the visible hardware does not support it.  Code 804 is the one that means "you bought the wrong GPU for this plan".

## Which number do you change?

The four numbers are not equally movable, and the cheapest repair is almost never the one people reach for.

![A decision graph from symptom to the single artifact that is wrong, with the repair for each](https://minio.canery.in/media/fig-07-which-number-four-cuda-version-numbers.png)

*Figure 7. Three of the five paths never touch the driver, which is the expensive change requiring a reboot and a change window.*

Figure 7 walks the diagnosis, and the ordering is deliberate: it asks which number is wrong before asking what to install.

**Nothing works and CUDA will not initialise.** A driver below the family minimum makes initialisation fail, reported as error 3 from the first call that touches a device.  Check the KMD against Figure 4's floors first, because this is the one case where the driver genuinely is the problem.

**A specific call fails with `cudaErrorCallRequiresNewerDriver`.** The runtime is fine and one feature is not. Either upgrade the driver or stop using that feature — and the error, value 36, tells you which class you are in without any further investigation.

**The application is a major version ahead of the driver.** Minor version compatibility does not apply across major families. On supported hardware, the forward-compatibility package bridges it; otherwise the choice is a driver upgrade or an older build of the application.

**`nvcc` disagrees with `nvidia-smi`.** This is not a fault. It is two artifacts reporting themselves correctly, and it was the most common search that led readers to this page. Nothing needs changing.

**You are choosing a wheel for a fixed host.** Read the runtime out of the wheel before installing it — the next section does exactly that — and compare it against the driver's ceiling. This is the only path here that prevents the failure rather than diagnosing it.

There is one thing no version change can buy, and it is worth stating because the reflex is strong: the Toolkit number does not participate. Installing a Toolkit does not raise the driver's ceiling, and removing one does not stop a wheel from running.

## The math: what the encoded number compares

Both version query functions return an integer rather than a string, encoded as **1000 × major + 10 × minor**.  CUDA 9.2 is `9020`; the runtime headers `torch` 2.14.0 resolves to define `CUDART_VERSION` as `13000`, which decodes to 13.0.  The current CUDA 13.4 headers define it as `13040`, and define `CUDA_VERSION` in `cuda.h` as the same `13040`.

The encoding exists so the comparison is a single integer test. Writing $r$ for the runtime constant compiled into your binary and $d$ for the ceiling the driver reports, the check that decides a launch is:

$$
\left\lfloor \frac{r}{1000} \right\rfloor = \left\lfloor \frac{d}{1000} \right\rfloor \quad\text{and}\quad d \ge m_{\lfloor r/1000 \rfloor}
$$

In words: the major versions must match, and the installed driver must clear that family's floor $m$ — the 450, 525 and 580 of Figure 4.  Note what is *not* in that expression. There is no term for the minor version of $r$ relative to $d$. That absence is exactly what minor version compatibility bought: before CUDA 11 the condition was the much stricter $d \ge r$, evaluated release by release.

Run the T4 case through it. The runtime constant is 13040 and the driver reports 13000, so the major versions agree at 13, and 580.65.06 clears the 580 floor. The condition holds, and $r > d$ — a newer runtime on an older driver — never enters into it.

The third digit does not appear either. A Toolkit's patch release, the `.Z` of NVIDIA's X.Y.Z scheme, is not encoded in these integers at all, which is consistent with its guarantee: patch releases change neither the API nor the ABI.

## Implementation: predict the answer before you install

Three of the four numbers are properties of files rather than of a running machine, so they can be read ahead of time. The lab script follows `torch`'s declared chain down to the runtime it will actually load:

```python
toolkit_pin = find_pin(info["requires_dist"], "cuda-toolkit")   # a meta-package
pinned = re.search(r"==\s*([\d.]+)", toolkit_pin).group(1)
inner = find_pin(pypi("cuda-toolkit", pinned)["info"]["requires_dist"],
                 "nvidia-cuda-runtime")
```

Then it reads the answer out of the C header that ships inside that wheel, rather than inferring it from a package name:

```python
found = re.search(r"#define\s+CUDART_VERSION\s+(\d+)", header_text)
raw = int(found.group(1))                     # 13000
print(f"CUDA {raw // 1000}.{(raw % 1000) // 10}")   # CUDA 13.0
```

None of that installs anything. The wheels are read over HTTP Range requests, so inspecting a 554 MB `torch` wheel costs about 1.2 MB of transfer.

The last step is the one that turns a quotation into evidence. Extract `libcudart.so.13`, load it with `ctypes`, and ask it directly:

```python
lib = ctypes.CDLL(path)                       # no GPU, no driver, no context
value = ctypes.c_int(0)
lib.cudaRuntimeGetVersion(ctypes.byref(value))
print(value.value)                            # 13000
```

That call answers on a machine with no NVIDIA hardware of any kind, which is the observable consequence of the version being a compile-time constant.  The load itself succeeds for a related reason: that library's `DT_NEEDED` list names no CUDA driver library at all, so the dynamic loader has nothing to fail to find.  The companion script reads the two host-side numbers the same way — procfs for the kernel module, and `cuDriverGetVersion` called inside `libcuda.so.1` — and deliberately never parses `nvidia-smi` output, because `nvidia-smi` is another reader of that driver rather than the source of anything.

## Limitations and common mistakes

![Six version strings from one pip install torch, each beside the namespace that produced it](https://minio.canery.in/media/fig-08-six-strings-four-cuda-version-numbers.png)

*Figure 8. One install, six strings, and only two of them are the CUDA version in the sense this post means.*

> [!WARNING]
> **The common mistake: reading `+cu130` as a dependency.** `torch` 2.14.0's `version.py` records `__version__ = '2.14.0+cu130'`,  while PyPI published that same distribution as `2.14.0` with no label in the wheel filename.  The `+cu130` is a PEP 440 local version label, and the specification is explicit that such labels carry no assigned semantics and that the Python Package Index must not allow them.  It is a build annotation. No resolver reads it, no driver check consults it, and treating it as a requirement for CUDA 13.0 on the host inverts the direction of the whole system.

Figure 8 lays out the rest of the collision. One `pip install torch` produces `2.14.0` from the index, `2.14.0+cu130` from `__version__`, `13.0` from `torch.version.cuda`, `13.0.3` from the `cuda-toolkit` pin,  `13.0.96` from the runtime component,  and `13000` from `CUDART_VERSION`.  Six strings, six namespaces, and no two of them are interchangeable.

**This post is about version compatibility only.** A binary that clears every check here can still fail because it carries no code image for your GPU's architecture. That is a different axis with a different error, and part 6 of this series owns it.

**Everything here is Linux.** On Windows, as of CUDA 13.0, the reported runtime version may not match the Toolkit the application was built with, because Windows uses the runtime packaged with the display driver.  The constant-in-the-binary reasoning above does not survive that, and this post does not cover it.

**Do not read `nvidia-smi`'s CUDA number as an inventory.** It reports the driver's ceiling. NVIDIA's own wording is that it is "usually, but not always" the Toolkit version installed  — and on a wheel-only machine it is not, because no Toolkit is installed at all.

**Every number here moves.** The PyPI pins were read on 2026-09-23, when the newest `cuda-toolkit` release was 13.4.2 — four minor versions ahead of what `torch` pinned.  Re-run the lab rather than trusting the transcript.

**This is a documented guarantee, not an inherent property.** The wider literature is a caution here: seven years of Maven Central releases showed roughly one third introducing at least one breaking change, at the same rate for minor releases as for major ones.  A study of over 70 million dependencies across 17 package managers found no evidence of large-scale migration to semantic versioning.  CUDA's guarantee is unusually well specified, which is why this post can state rules at all — but the reason tooling that prevents compatibility failures works by checking declared ranges against what the installed binary actually offers, rather than trusting version strings, applies here too.  Read the artifact.

## Key takeaways

- **`nvidia-smi`'s CUDA number is a ceiling, not an inventory.** NVIDIA renamed the field to `CUDA UMD Version` for exactly this reason.
- **The runtime version is a compile-time constant**, and it answers on a machine with no driver.  Nothing negotiates at run time; there is one comparison.
- **Minor version compatibility is three numbers, not a matrix**: driver 450 for CUDA 11.x, 525 for 12.x, 580 for 13.x.  It carries exactly three caveats, and PTX is the one that catches people.
- **The forward-compatibility package spans a different gap** — kernel driver to CUDA driver — and requires datacenter-class hardware, an `LD_LIBRARY_PATH` you set yourself, and giving up graphics interop.
- **`nvcc`'s version takes no part in whether a pre-built wheel runs.** It is the most-checked number and the least relevant one.

## Try it yourself

<details><summary>A wheel needs CUDA 12.4 and the host driver reports 12.2. Does it run?</summary>

Yes, provided the driver is 525 or newer. Both are inside the 12.x family, so minor version compatibility applies and the runtime being *ahead* of the driver's ceiling is exactly the case it was built for. The answer changes if the application compiles device code to PTX, or uses a feature that spans Toolkit and driver — then you get `cudaErrorCallRequiresNewerDriver` and need the newer driver after all.

</details>

<details><summary>Same wheel, but the host driver is from the 11 series. Does the compatibility package help?</summary>

Only on data center GPUs, select NGC Server Ready RTX SKUs, or Jetson boards. On anything else the package is not supported, and code 804 is what you get for trying. Even where it is supported, installing it changes nothing until `LD_LIBRARY_PATH` points at the `compat` directory, and CUDA–OpenGL interop will not work afterwards.

</details>

<details><summary>Why can the lab read the runtime version with no GPU present?</summary>

Because since CUDA 12.0 `cudaRuntimeGetVersion` does not initialise CUDA — it returns a constant compiled into `libcudart`. The lab proves it rather than asserting it: it extracts the library from the wheel, loads it with `ctypes` on a driverless machine, and gets `13000` back.

</details>

## References

### Lab downloads

- [`README.md`](LAB_01) — hardware tier, prerequisites, run order, expected results, and cleanup.
- [`wheelio.py`](LAB_02) — shared helpers: PyPI metadata, an HTTP Range file object, and a minimal ELF64 dynamic-section reader.
- [`cuda_versions.py`](LAB_03) — follows a framework's pin chain to its CUDA runtime, reads the version macros from the shipped headers, then loads the library and asks it directly.
- [`check_host.py`](LAB_04) — prints the four numbers for the machine you run it on, each from the artifact that owns it.
- [`expected-output.txt`](LAB_05) — both transcripts as captured on a machine with no NVIDIA GPU, dated.
- Lab Download link: [Lab Download](https://minio.canery.in/media/lab-four-cuda-version-numbers.zip)

### Sources

**NVIDIA documentation**

- CUDA Compatibility — *Minor Version Compatibility*. [https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html) (accessed 2026-09-23)
- CUDA Compatibility — *Forward Compatibility*. [https://docs.nvidia.com/deploy/cuda-compatibility/forward-compatibility.html](https://docs.nvidia.com/deploy/cuda-compatibility/forward-compatibility.html) (accessed 2026-09-23)
- CUDA Toolkit Release Notes, Table 3. [https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html) (accessed 2026-09-23)
- System Management Interface (`nvidia-smi`), field definitions. [https://docs.nvidia.com/deploy/nvidia-smi/index.html](https://docs.nvidia.com/deploy/nvidia-smi/index.html) (accessed 2026-09-23)
- CUDA C++ Best Practices Guide §16, *CUDA Compatibility Developer's Guide*. [https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html) (accessed 2026-09-23)

**Shipped artifacts**

- `cuda.h`, `cuda_runtime_api.h` and `driver_types.h` from the `nvidia-cuda-runtime` 13.4.92 wheel. [https://pypi.org/project/nvidia-cuda-runtime/13.4.92/](https://pypi.org/project/nvidia-cuda-runtime/13.4.92/) (accessed 2026-09-23)
- `nvidia-cuda-runtime` 13.0.96 wheel — headers and the `libcudart.so.13` ELF dynamic section. [https://pypi.org/project/nvidia-cuda-runtime/13.0.96/](https://pypi.org/project/nvidia-cuda-runtime/13.0.96/) (accessed 2026-09-23)
- `torch` 2.14.0 wheel — `torch/version.py` and release metadata. [https://pypi.org/project/torch/2.14.0/](https://pypi.org/project/torch/2.14.0/) (accessed 2026-09-23)

**Standards and literature**

- PyPA, *Version specifiers* (PEP 440 is its historical document). [https://packaging.python.org/en/latest/specifications/version-specifiers/](https://packaging.python.org/en/latest/specifications/version-specifiers/) (accessed 2026-09-23)
- Raemaekers, van Deursen, Visser, "Semantic Versioning versus Breaking Changes: A Study of the Maven Repository", IEEE SCAM 2014. [https://doi.org/10.1109/SCAM.2014.30](https://doi.org/10.1109/SCAM.2014.30)
- Dietrich, Pearce, Stringer, Tahir, "Dependency Versioning in the Wild", IEEE/ACM MSR 2019. [https://doi.org/10.1109/MSR.2019.00061](https://doi.org/10.1109/MSR.2019.00061)
- Jia, Li, Yu, Zeng, "DepOwl: Detecting Dependency Bugs to Prevent Compatibility Failures", IEEE/ACM ICSE 2021. [https://doi.org/10.1109/ICSE43902.2021.00021](https://doi.org/10.1109/ICSE43902.2021.00021)
- Ponomarenko, Rubanov, "Automated Verification of Shared Libraries for Backward Binary Compatibility", IEEE VALID 2010. [https://doi.org/10.1109/VALID.2010.27](https://doi.org/10.1109/VALID.2010.27)
