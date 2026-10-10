# Source ledger — four-cuda-version-numbers

Series: nvidia-stack, part 2. Tier L2 — floors are 4 peer-reviewed or standard sources carrying
an identifier, and 3 distinct scholarly databases in the search log.

Every NVIDIA version number, driver range and error code below was read out of the primary
artifact on **2026-09-23**, not recalled. Where a number can move — a PyPI release, a
documentation table — the Condition column says so and names the date it was read.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S01 | T1 | Raemaekers, van Deursen, Visser, "Semantic Versioning versus Breaking Changes: A Study of the Maven Repository" | IEEE SCAM | 2014 | 10.1109/SCAM.2014.30 | peer-reviewed | https://doi.org/10.1109/SCAM.2014.30 | 2026-09-23 |
| S02 | T1 | Dietrich, Pearce, Stringer, Tahir, "Dependency Versioning in the Wild" | IEEE/ACM MSR | 2019 | 10.1109/MSR.2019.00061 | peer-reviewed | https://doi.org/10.1109/MSR.2019.00061 | 2026-09-23 |
| S03 | T1 | Jia, Li, Yu, Zeng, "DepOwl: Detecting Dependency Bugs to Prevent Compatibility Failures" | IEEE/ACM ICSE | 2021 | 10.1109/ICSE43902.2021.00021 | peer-reviewed | https://doi.org/10.1109/ICSE43902.2021.00021 | 2026-09-23 |
| S04 | T1 | Ponomarenko, Rubanov, "Automated Verification of Shared Libraries for Backward Binary Compatibility" | IEEE VALID | 2010 | 10.1109/VALID.2010.27 | peer-reviewed | https://doi.org/10.1109/VALID.2010.27 | 2026-09-23 |
| S05 | T1 | PyPA, "Version specifiers" (the living specification; PEP 440 is now its historical document) | Python Packaging Authority | 2026 | PEP 440 | standard | https://packaging.python.org/en/latest/specifications/version-specifiers/ | 2026-09-23 |
| S06 | T2 | NVIDIA, "CUDA Compatibility" — *Minor Version Compatibility* | NVIDIA docs | 2026 | — | official-docs | https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html | 2026-09-23 |
| S07 | T2 | NVIDIA, "CUDA Compatibility" — *Forward Compatibility* | NVIDIA docs | 2026 | — | official-docs | https://docs.nvidia.com/deploy/cuda-compatibility/forward-compatibility.html | 2026-09-23 |
| S08 | T2 | NVIDIA, "CUDA Toolkit Release Notes", Table 3 | NVIDIA docs | 2026 | — | official-docs | https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html | 2026-09-23 |
| S09 | T2 | NVIDIA, "System Management Interface (nvidia-smi)" | NVIDIA docs | 2026 | — | official-docs | https://docs.nvidia.com/deploy/nvidia-smi/index.html | 2026-09-23 |
| S10 | T2 | NVIDIA, "CUDA C++ Best Practices Guide" §16, *CUDA Compatibility Developer's Guide* | NVIDIA docs | 2026 | — | official-docs | https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html | 2026-09-23 |
| S11 | T3 | `cuda_runtime_api.h` inside the `nvidia-cuda-runtime` 13.4.92 wheel | PyPI | 2026 | nvidia-cuda-runtime 13.4.92 | source | https://pypi.org/project/nvidia-cuda-runtime/13.4.92/ | 2026-09-23 |
| S12 | T3 | `cuda.h` inside the same `nvidia-cuda-runtime` 13.4.92 wheel | PyPI | 2026 | nvidia-cuda-runtime 13.4.92 | source | https://pypi.org/project/nvidia-cuda-runtime/13.4.92/ | 2026-09-23 |
| S13 | T3 | `driver_types.h` inside the same `nvidia-cuda-runtime` 13.4.92 wheel | PyPI | 2026 | nvidia-cuda-runtime 13.4.92 | source | https://pypi.org/project/nvidia-cuda-runtime/13.4.92/ | 2026-09-23 |
| S14 | T3 | `nvidia-cuda-runtime` 13.0.96 wheel — headers and `libcudart.so.13` ELF dynamic section | PyPI | 2026 | nvidia-cuda-runtime 13.0.96 | source | https://pypi.org/project/nvidia-cuda-runtime/13.0.96/ | 2026-09-23 |
| S15 | T3 | `torch/version.py` inside the `torch` 2.14.0 manylinux wheel | PyPI | 2026 | torch 2.14.0 | source | https://pypi.org/project/torch/2.14.0/ | 2026-09-23 |
| S16 | T3 | PyPI JSON API — `torch` 2.14.0 `requires_dist` | PyPI | 2026 | torch 2.14.0 | source | https://pypi.org/pypi/torch/json | 2026-09-23 |
| S17 | T3 | PyPI JSON API — `cuda-toolkit` 13.0.3 `requires_dist` | PyPI | 2026 | cuda-toolkit 13.0.3 | source | https://pypi.org/pypi/cuda-toolkit/13.0.3/json | 2026-09-23 |
| S18 | T3 | PyPI JSON API — `cuda-toolkit` current release | PyPI | 2026 | cuda-toolkit 13.4.2 | source | https://pypi.org/pypi/cuda-toolkit/json | 2026-09-23 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | Crossref | `semantic versioning breaking changes empirical` | Raemaekers 2014 (SCAM) and Ochoa 2022 (EMSE) as the two central papers; both carry DOIs |
| 2 | 1 | Crossref | `binary compatibility shared libraries evolution` | Ponomarenko 2010 (VALID) and the 2009 CEE-SECR companion paper; the topic's literature is thin and old |
| 3 | 1 | Crossref | `dependency versioning in the wild` | Dietrich 2019 (MSR), the 70-million-dependency study across 17 package managers |
| 4 | 1 | Crossref | `DepOwl detecting dependency bugs compatibility failures` | Jia 2021, ICSE, DOI 10.1109/ICSE43902.2021.00021 |
| 5 | 1 | Crossref | `compatibility issues dynamic link libraries empirical study` | mostly Android API-evolution work; nothing on native loader-level version checks, so the rung stopped here |
| 6 | 1 | Crossref | DOI lookups on the four candidates for authors, venue and year | confirmed all four venues and author lists; no preprint-only entries among them |
| 7 | 1 | OpenAlex | full-text search `binary compatibility shared libraries versioning` | dominated by software-citation records (R, SciPy, pymatgen); full-text search is the wrong instrument here |
| 8 | 1 | OpenAlex | `filter=title.search:backward binary compatibility libraries` sorted by citations | confirmed Ponomarenko 2010 at 7 citations and the 2009 paper at 1 — the sub-field is genuinely small |
| 9 | 1 | OpenAlex | abstract reconstruction for the four accepted DOIs | gave verified abstracts for S01, S02 and S03; Ochoa 2022 has none indexed, so it was dropped rather than cited from its title |
| 9b | 1 | OpenAlex | `cites:W2163048279` — forward chase from Raemaekers 2014, sorted by citations | 139 citing works; the two central follow-ups are Kula 2017 (EMSE, *Do developers update their library dependencies?*) and Brito 2017 on API breaking-change impact. Neither was needed: the post's framing claim is already carried by S01 and S02, and both follow-ups are about API rather than ABI breakage |
| 9c | 1 | Crossref | `breaking changes software ecosystems systematic literature review` — the survey step, run before the individual papers were accepted | no survey covers vendor GPU driver versioning; the ecosystem SLRs returned are all about governance and packaging, which is why this post rests on NVIDIA's own specification rather than on literature |
| 10 | 1 | Google Scholar (via web search) | `empirical study binary compatibility breakage shared library versioning Linux` | surfaced DepOwl and a Stack Overflow-based compatibility study; confirmed no survey paper covers vendor GPU driver versioning |
| 11 | 1 | arXiv API | `all:"dependency conflicts"` | zero entries returned; arXiv is not where this literature sits |
| 12 | 1 | Semantic Scholar API | `library version compatibility empirical study` | HTTP 429 rate limit on two attempts; abandoned in favour of OpenAlex for abstracts |
| 13 | 2 | NVIDIA docs | CUDA Compatibility → *Minor Version Compatibility* | the driver-range table, the three caveats, and the worked `nvidia-smi` / `deviceQuery` disagreement |
| 14 | 2 | NVIDIA docs | CUDA Compatibility → *Forward Compatibility* | the hardware precondition list, the package contents, the support matrix, and the two error codes |
| 15 | 2 | NVIDIA docs | CUDA C++ Best Practices Guide §16 | the X.Y.Z scheme, Enhanced Compatibility's origin in 11.1, and the versioned C-style ABI statement |
| 16 | 3 | NVIDIA docs | CUDA Toolkit Release Notes, driver tables | Table 3 restates the minor-compatibility ranges; Table 4 covers 12.9 and earlier only |
| 17 | 3 | NVIDIA docs | nvidia-smi documentation, field definitions | `Driver Version` and `CUDA Version` are both deprecated; `KMD Version` and `CUDA UMD Version` replace them |
| 18 | 5 | PyPI JSON API | `torch`, `cuda-toolkit`, `nvidia-cuda-runtime` release metadata | the pin chain torch 2.14.0 → cuda-toolkit 13.0.3 → nvidia-cuda-runtime 13.0.96 |
| 19 | 5 | PyPI wheel, HTTP Range | `cuda.h`, `cuda_runtime_api.h`, `driver_types.h` from two runtime wheels | the version macros and every error-code constant, read from the shipped headers |
| 20 | 5 | PyPI wheel, HTTP Range | `torch/version.py` from the torch 2.14.0 wheel | `__version__ = '2.14.0+cu130'` and `cuda = '13.0'` |
| 21 | 4 | PyPA specs | `version-specifiers` source on GitHub | local version labels carry no assigned semantics and PyPI must not allow them — the `+cu130` trap |
| 22 | 4 | NVIDIA docs | nvidia-smi changelog, field rename entry | the rename is recorded as deliberate, "to more accurately reflect the source of the version information" |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | `nvidia-smi`'s `Driver Version` field is deprecated in favour of `KMD Version` | S09 | as documented on 2026-09-23 |
| L02 | `nvidia-smi`'s `CUDA Version` field is deprecated in favour of `CUDA UMD Version` | S09 | as documented on 2026-09-23 |
| L03 | `CUDA UMD Version` is defined as the latest CUDA version the driver supports, and is usually but not always the toolkit version installed on the system | S09 | NVIDIA's own wording; "usually but not always" is theirs, not a hedge of ours |
| L04 | `KMD Version` is the version of the installed kernel-mode driver, which is the NVIDIA display driver | S09 | — |
| L05 | NVIDIA describes the rename as making the fields reflect the source of the version information more accurately | S09 | from the nvidia-smi changelog; no release number is given in the entry |
| L06 | `cudaDriverGetVersion` returns the latest CUDA version supported by the driver, and returns 0 when no driver is installed | S11 | header doc comment, CUDA 13.4 |
| L07 | Both version query functions encode the answer as 1000 × major + 10 × minor | S11 | stated for both functions in the shipped header |
| L08 | As of CUDA 12.0, `cudaRuntimeGetVersion` no longer initializes CUDA and returns a compile-time constant naming the Toolkit version | S11 | header doc comment, CUDA 13.4 |
| L09 | As of CUDA 13.0 on Windows, the reported runtime version may differ from the Toolkit the application was built with, because Windows uses the runtime packaged with the display driver | S11 | Windows only; the post states the platform |
| L10 | `cuda_runtime_api.h` in `nvidia-cuda-runtime` 13.4.92 defines `CUDART_VERSION` as 13040 | S11 | that wheel, read 2026-09-23 |
| L11 | `cuda.h` in the same wheel defines `CUDA_VERSION` as 13040 | S12 | same wheel |
| L12 | `nvidia-cuda-runtime` 13.0.96 — the build `torch` 2.14.0 resolves to — defines `CUDART_VERSION` as 13000 | S14 | that wheel; the resolution is S17's pin |
| L13 | `libcudart.so.13` in that wheel carries SONAME `libcudart.so.13` and names no CUDA driver library in `DT_NEEDED` | S14 | ELF dynamic section of the shipped library |
| L14 | `torch` 2.14.0 records `__version__ = '2.14.0+cu130'` and `cuda = '13.0'` in `torch/version.py` | S15 | the manylinux x86-64 wheel published on PyPI |
| L15 | That same distribution is published on PyPI as version `2.14.0`, with no local label in the wheel filename | S16 | PyPI release files, 2026-09-23 |
| L16 | `torch` 2.14.0 declares `cuda-toolkit[cublas,cudart,…]==13.0.3` on Linux | S16 | current release metadata, 2026-09-23 |
| L17 | `cuda-toolkit` 13.0.3 pins `nvidia-cuda-runtime==13.0.96.*` | S17 | that release's metadata |
| L18 | The newest `cuda-toolkit` release on PyPI is 13.4.2, four minor versions ahead of what `torch` pins | S18 | read 2026-09-23; this moves |
| L19 | CUDA 13.x requires driver ≥ 580; CUDA 12.x ≥ 525 with an upper bound below 580; CUDA 11.x ≥ 450 with an upper bound below 525 | S06, S08 | the upper bounds apply to minor version compatibility only; newer drivers stay supported through backward compatibility |
| L20 | From CUDA 11 onward, an application built with any toolkit in a major family runs, with a limited feature set, on any system meeting that family's minimum driver | S06 | the minimum driver may differ from the driver packaged with the toolkit, but belongs to the same major release |
| L21 | Minor version compatibility carries three documented caveats: features that span toolkit and driver, applications that compile device code to PTX, and the requirement to pass a target architecture to `nvcc` | S06 | NVIDIA lists exactly these three |
| L22 | A feature that needs a newer driver reports `cudaErrorCallRequiresNewerDriver` | S06, S13 | the name is in the doc; the value 36 is from `driver_types.h` |
| L23 | `cudaErrorInsufficientDriver` is 35, `cudaErrorCallRequiresNewerDriver` is 36, and `cudaErrorInitializationError` is 3 | S13 | CUDA 13.4 headers |
| L24 | `CUDA_ERROR_SYSTEM_DRIVER_MISMATCH` (803) means the display driver and CUDA driver versions disagree; `CUDA_ERROR_COMPAT_NOT_SUPPORTED_ON_DEVICE` (804) means the system was upgraded for forward compatibility but the hardware CUDA can see does not support it | S12, S07 | the doc names them as the forward-compatibility check; the values are from `cuda.h` |
| L25 | A driver below the minimum makes CUDA initialization fail, which the runtime reports as error 3 from the first call that touches a device | S06, S10 | both documents show the same `deviceQuery` transcript |
| L26 | Forward compatibility is supported only on NVIDIA Data Center GPUs, select NGC Server Ready SKUs of RTX cards, and Jetson boards | S07 | this is the precondition most readers miss; an ordinary consumer card is not on the list |
| L27 | The package is named `cuda-compat-<major>-<minor>` and installs into `/usr/local/cuda-<version>/compat` | S07 | — |
| L28 | `cuda-compat-13-4` is built from NVIDIA driver libraries version 615 | S07 | stated as the example in the doc |
| L29 | The package ships libraries only and does not configure the system to find them; `LD_LIBRARY_PATH` is the documented step | S07 | NVIDIA's own note |
| L30 | Forward compatibility is defined between the kernel driver and the CUDA driver, whereas minor version compatibility is defined between the CUDA runtime and the CUDA driver | S07 | the single sentence the whole mechanism turns on |
| L31 | The package contains `libcuda.so.*`, `libcudadebugger.so.*`, `libnvidia-nvvm*.so.*`, `libnvidia-ptxjitcompiler.so.*` and `libnvidia-pkcs11*.so.*`, with `libnvidia-gpucomp.so.*` and `libnvidia-tileiras.so.*` added at CUDA 13.4 | S07 | contents list as published on 2026-09-23 |
| L32 | NVIDIA's support matrix pairs driver 535 with CUDA 12.2, 570 with 12.8, 580 with 13.0, 590 with 13.1, 595 with 13.2, 610 with 13.3 and 615 with 13.4 | S07 | Table 3 of the forward-compatibility page; branches not listed are end of life |
| L33 | An older forward-compatibility package is not supported on a newer driver | S07 | the reason a full system upgrade must remove the package |
| L34 | CUDA–OpenGL and CUDA–Vulkan interop does not work under any forward-compatibility package | S07 | Table 4, all three major families |
| L35 | From CUDA 11 the toolkit follows an X.Y.Z scheme in which a major change breaks binary compatibility and a minor change maintains it | S10 | §16.1 |
| L36 | CUDA Enhanced Compatibility arrived in CUDA 11.1 and relaxed the runtime's minimum driver version check | S10 | §16.1 |
| L37 | The forward-compatible upgrade path was introduced in CUDA 10 | S10 | §16.1 |
| L38 | The CUDA driver API has a versioned C-style ABI: binary compatible across driver versions, not source compatible across SDK releases | S10 | §16.2 and §16.3 |
| L39 | Applications compiled with toolkits as old as CUDA 3.2 still run on modern drivers | S10 | §16.1, NVIDIA's own example of the backward guarantee |
| L40 | Before CUDA 11.0 the minimum driver for a toolkit was the driver shipped with it, so every minor toolkit bump forced a driver upgrade | S10, S06 | the reason the pre-11 experience is not a guide to the current one |
| L41 | A PEP 440 local version label carries no assigned semantics, and the Python Package Index must not allow one | S05 | §"Local version identifiers"; the rule is normative |
| L42 | Seven years of Maven Central releases show roughly one third introducing at least one breaking change, at the same rate for minor as for major releases | S01 | one ecosystem, Java, and API-level breakage rather than ABI |
| L43 | A study of over 70 million dependencies across 17 package managers found no evidence of large-scale migration to semantic versioning | S02 | declared practice across ecosystems, not a claim about CUDA |
| L45 | NVIDIA's worked transcript: a Tesla T4 on driver 580.65.06, where `nvidia-smi` reports CUDA Version 13.0 and `deviceQuery` reports Driver / Runtime 13.0 / 13.4 with `Result = PASS` | S06 | NVIDIA's own published transcript, not our measurement; we have no GPU |
| L44 | Tooling that prevents compatibility failures works by checking the declared version range against what the installed binary actually offers, rather than trusting the version string | S03, S04 | DepOwl prevented 35 of 38 known failures drawn from Stack Overflow and found 77 unknown dependency bugs in one distribution's repository |

## Open questions

- **Which `nvidia-smi` release renamed the fields.** The changelog entry is present and
  unambiguous, but the release it sits under could not be pinned from the rendered page. The post
  therefore says the fields *are* deprecated, and never says when that happened.
- **Whether `torch.version.cuda` can ever disagree with the runtime the wheel resolves.** For
  2.14.0 they agree at 13.0, and the mechanism that would make them disagree is plausible but was
  not observed. The post states the agreement for this build and does not generalise it.
- **Windows.** `cudaRuntimeGetVersion`'s CUDA 13.0 Windows caveat is recorded (L09) but not
  explored; every lab and every transcript in this post is Linux.
- **The forward chase found two papers the post does not cite.** Kula et al. 2017 (EMSE) and
  Brito et al. 2017 both bear on how declared versions behave in practice, and both are about
  *API* breakage in source ecosystems rather than the *ABI* and loader-level checks this post is
  about. They are recorded here so a later part in the compatibility thread does not re-run the
  same search.

## Corrections carried forward from part 1

Part 1's re-verification on 2026-09-23 found two failed claims of the shapes "X omits Y" and
"there are exactly N". Both shapes appear naturally in this part — "the compat package contains
exactly these files", "there are exactly three caveats". Every such claim here (L21, L31, L32,
L34) was read from the live document on the access date and carries that date in its Condition.
